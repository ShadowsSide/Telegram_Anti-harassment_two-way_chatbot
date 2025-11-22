import ipaddress
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .state import user_data
from .tasks import do_ping_in_background, do_nexttrace_in_background
from .utils import schedule_delete_message
from .config import SERVERS, save_config
import asyncio

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        return False  # 不是网络测试的回调，返回 False 让其他处理器处理

    data = query.data
    
    # 只处理以 nt_ 开头的回调（网络测试相关）
    if not data.startswith("nt_"):
        return False

    info = user_data[user_id]
    chat_id = info["chat_id"]
    message_id = info["message_id"]

    # 处理安装NextTrace的回调
    if data.startswith("nt_installnexttrace_"):
        if info.get("operation") != "installnexttrace":
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="当前操作不支持安装NextTrace。"
            )
            return True
            
        if data == "nt_installnexttrace_cancel":
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="已取消安装 NextTrace 操作。"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True
            
        # 解析服务器索引
        server_idx = int(data.split("_")[2])
        
        if server_idx < 0 or server_idx >= len(SERVERS):
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="无效的服务器索引，可能服务器列表已更新，请重新执行 /install_nexttrace 命令。"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True
            
        server_info = SERVERS[server_idx]
        
        # 显示安装中消息
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"正在服务器 {server_info['name']} 上安装 NextTrace...\n请耐心等待，这可能需要一些时间。"
        )
        
        # 执行安装命令
        from .network import install_nexttrace_on_server
        try:
            result = await asyncio.to_thread(install_nexttrace_on_server, server_info)
            
            # 显示安装结果
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"在服务器 {server_info['name']} 上安装 NextTrace 的结果：\n\n{result}"
            )
        except Exception as e:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"在服务器 {server_info['name']} 上安装 NextTrace 时出错：\n\n{str(e)}"
            )
        
        # 5秒后删除消息
        context.application.create_task(
            schedule_delete_message(context, chat_id, message_id, delay=15)  # 安装结果显示时间更长
        )
        del user_data[user_id]
        return True

    # 处理服务器删除回调
    if data.startswith("nt_rmserver_"):
        if info.get("operation") != "rmserver":
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="当前操作不支持删除服务器。"
            )
            return True
            
        if data == "nt_rmserver_cancel":
            # 编辑现有消息，然后5秒后删除它
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="已取消删除服务器操作。"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True
            
        # 检查确认状态
        if info.get("confirm_delete"):
            # 已经确认，执行删除
            server_idx = int(info["server_idx"])
            
            if server_idx < 0 or server_idx >= len(SERVERS):
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="无效的服务器索引，可能服务器列表已更新，请重新执行 /rmserver 命令。"
                )
                # 5秒后删除消息
                context.application.create_task(
                    schedule_delete_message(context, chat_id, message_id, delay=5)
                )
                del user_data[user_id]
                return True
                
            removed_server = SERVERS.pop(server_idx)
            save_config()
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"成功删除服务器：{removed_server['name']} (host={removed_server['host']})"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True
            
        # 第一次点击，显示确认选项
        if data.startswith("nt_rmserver_") and data != "nt_rmserver_cancel" and data != "nt_rmserver_confirm" and data != "nt_rmserver_abort":
            server_idx = int(data.split("_")[2])
            
            if server_idx < 0 or server_idx >= len(SERVERS):
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="无效的服务器索引，可能服务器列表已更新，请重新执行 /rmserver 命令。"
                )
                # 5秒后删除消息
                context.application.create_task(
                    schedule_delete_message(context, chat_id, message_id, delay=5)
                )
                del user_data[user_id]
                return True
                
            server_info = SERVERS[server_idx]
            
            # 保存要删除的服务器索引
            info["server_idx"] = server_idx
            
            # 显示确认对话框
            keyboard = [
                [
                    InlineKeyboardButton("确认删除", callback_data="nt_rmserver_confirm"),
                    InlineKeyboardButton("取消", callback_data="nt_rmserver_abort")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"你确定要删除以下服务器吗？\n\n名称: {server_info['name']}\nHost: {server_info['host']}:{server_info['port']}\n\n此操作不可撤销！",
                reply_markup=reply_markup
            )
            return True
        
        # 处理确认和取消按钮
        if data == "nt_rmserver_confirm":
            info["confirm_delete"] = True
            
            server_idx = info["server_idx"]
            server_info = SERVERS[server_idx]
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"正在删除服务器：{server_info['name']}..."
            )
            
            # 执行删除
            removed_server = SERVERS.pop(server_idx)
            save_config()
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"成功删除服务器：{removed_server['name']} (host={removed_server['host']})"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True
            
        if data == "nt_rmserver_abort":
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="已取消删除服务器操作。"
            )
            # 5秒后删除消息
            context.application.create_task(
                schedule_delete_message(context, chat_id, message_id, delay=5)
            )
            del user_data[user_id]
            return True

    # 处理trace_mode选择
    if data.startswith("nt_trace_mode_"):
        if info.get("operation") != "nexttrace":
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                              text="当前操作不支持选择追踪模式。")
            return True
        
        trace_mode = "icmp" if data == "nt_trace_mode_icmp" else "tcp"
        info["trace_mode"] = trace_mode
        
        # 选择好模式后，继续选择服务器
        keyboard = []
        for idx, server_info in enumerate(SERVERS):
            btn = InlineKeyboardButton(server_info['name'], callback_data=f"nt_server_{idx}")
            keyboard.append([btn])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id,
            text=f"你选择了{('ICMP' if trace_mode == 'icmp' else 'TCP')}模式追踪，请选择服务器：",
            reply_markup=reply_markup
        )
        return True

    if data.startswith("nt_server_"):
        idx = int(data.split("_")[2])
        if idx < 0 or idx >= len(SERVERS):
            await context.bot.edit_message_text("无效的服务器下标。", chat_id=chat_id, message_id=message_id)
            return True

        server_info = SERVERS[idx]
        info["server_info"] = server_info
        if info.get("operation") == "ping":
            mode = info["mode"]
            if mode == "cmd":
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="已收到请求，正在后台执行 Ping 操作，请稍候..."
                )
                context.application.create_task(
                    do_ping_in_background(context, chat_id, server_info, info["target"], info["count"], user_id)
                )
            elif mode == "interactive":
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"你选择了 {server_info['name']}。\n请发送目标IP或域名（例如：8.8.8.8 或 google.com）。"
                )
        elif info.get("operation") == "nexttrace":
            mode = info["mode"]
            if mode == "cmd":
                try:
                    ipaddress.ip_address(info["target"])
                    trace_mode = info.get("trace_mode", "icmp")  # 默认为icmp
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']} 为IP地址，正在后台执行{('ICMP' if trace_mode == 'icmp' else 'TCP')}模式路由追踪操作，请稍候..."
                    )
                    context.application.create_task(
                        do_nexttrace_in_background(context, chat_id, server_info, info["target"], "direct", user_id, trace_mode)
                    )
                except ValueError:
                    keyboard = [
                        [
                            InlineKeyboardButton("IPv4", callback_data="nt_iptype_ipv4"),
                            InlineKeyboardButton("IPv6", callback_data="nt_iptype_ipv6")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']}\n请选择 IP 协议类型：",
                        reply_markup=reply_markup
                    )
            elif mode == "interactive":
                try:
                    ipaddress.ip_address(info["target"])
                    trace_mode = info.get("trace_mode", "icmp")  # 默认为icmp
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n目标： {info['target']} 为IP地址，正在后台执行{('ICMP' if trace_mode == 'icmp' else 'TCP')}模式路由追踪操作，请稍候..."
                    )
                    context.application.create_task(
                        do_nexttrace_in_background(context, chat_id, server_info, info["target"], "direct", user_id, trace_mode)
                    )
                except ValueError:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"你选择了 {server_info['name']}。\n请发送目标IP或域名。"
                    )
        return True
    elif data.startswith("nt_count_"):
        if info.get("operation") != "ping":
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="当前操作不支持选择 Ping 次数。")
            return True

        count = int(data.split("_")[2])
        info["count"] = count
        if not info.get("server_info") or not info.get("target"):
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="服务器或目标IP信息不完整，请重新开始 /ping 流程。")
            return True

        await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                            text="已收到请求，正在后台执行 Ping 操作，请稍候...")
        context.application.create_task(
            do_ping_in_background(context, chat_id, info["server_info"], info["target"], count, user_id)
        )
        return True
    elif data.startswith("nt_iptype_"):
        if info.get("operation") != "nexttrace":
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                  text="当前操作不支持 IP 协议类型选择。")
            return True
        ip_type = "IPv4" if data == "nt_iptype_ipv4" else "IPv6"
        info["ip_type"] = ip_type
        trace_mode = info.get("trace_mode", "icmp")  # 默认为icmp
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text=f"已收到请求，正在后台执行{('ICMP' if trace_mode == 'icmp' else 'TCP')}模式路由追踪操作，请稍候..."
        )
        context.application.create_task(
            do_nexttrace_in_background(context, chat_id, info["server_info"], info["target"], ip_type, user_id, trace_mode)
        )
        return True
    
    return False  # 不是网络测试的回调

async def handle_message(update, context):
    user_id = update.effective_user.id
    if user_id not in user_data:
        return False  # 不是网络测试的消息，返回 False 让其他处理器处理
    
    info = user_data[user_id]
    
    # 处理添加服务器的交互流程
    if info.get("operation") == "addserver":
        text = update.message.text.strip()
        
        # 检查是否是取消命令
        if text.lower() == "/cancel":
            # 删除上一条提示消息
            if info.get("prompt_message_id"):
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=info["prompt_message_id"]
                    )
                except Exception:
                    pass  # 忽略删除失败的错误
                    
            del user_data[user_id]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ 已取消添加服务器操作。"
            )
            return True
            
        step = info.get("step", 1)
        server_data = info.get("server_data", {})
        
        # 删除用户输入的消息，保持界面整洁
        context.application.create_task(schedule_delete_message(context, update.message.chat_id, update.message.message_id, delay=2))
        
        # 删除上一条提示消息
        if info.get("prompt_message_id"):
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=info["prompt_message_id"]
                )
            except Exception:
                pass  # 忽略删除失败的错误
        
        if step == 1:  # 处理服务器名称
            server_data["name"] = text
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"步骤 2/5: 服务器名称已设置为 \"{text}\"。\n\n请输入服务器IP地址：\n\n🔹 输入 /cancel 可随时取消"
            )
            info["step"] = 2
            info["server_data"] = server_data
            info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
            
        elif step == 2:  # 处理服务器IP地址
            server_data["host"] = text
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"步骤 3/5: 服务器IP已设置为 \"{text}\"。\n\n请输入SSH端口号（通常为22）：\n\n🔹 输入 /cancel 可随时取消"
            )
            info["step"] = 3
            info["server_data"] = server_data
            info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
            
        elif step == 3:  # 处理端口号
            try:
                port = int(text)
                server_data["port"] = port
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"步骤 4/5: 端口号已设置为 {port}。\n\n请输入SSH用户名：\n\n🔹 输入 /cancel 可随时取消"
                )
                info["step"] = 4
                info["server_data"] = server_data
                info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
            except ValueError:
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="端口号必须是数字，请重新输入端口号：\n\n🔹 输入 /cancel 可随时取消"
                )
                info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
                
        elif step == 4:  # 处理用户名
            server_data["username"] = text
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"步骤 5/5: 用户名已设置为 \"{text}\"。\n\n请输入SSH密码：\n\n🔹 输入 /cancel 可随时取消"
            )
            info["step"] = 5
            info["server_data"] = server_data
            info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
            
        elif step == 5:  # 处理密码并完成添加
            server_data["password"] = text
            
            # 显示确认信息
            summary = (
                f"请确认以下服务器信息：\n\n"
                f"名称: {server_data['name']}\n"
                f"主机: {server_data['host']}\n"
                f"端口: {server_data['port']}\n"
                f"用户名: {server_data['username']}\n"
                f"密码: {'*' * len(server_data['password'])}\n\n"
                f"确认添加吗？(输入 yes 确认，输入其他内容取消)"
            )
            
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=summary
            )
            
            info["step"] = 6
            info["server_data"] = server_data
            info["prompt_message_id"] = msg.message_id  # 保存当前提示消息ID
            
        elif step == 6:  # 确认添加
            # 删除确认提示消息
            if info.get("prompt_message_id"):
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=info["prompt_message_id"]
                    )
                except Exception:
                    pass
                    
            if text.lower() == "yes":
                # 添加服务器到配置
                SERVERS.append(server_data)
                save_config()
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"服务器添加成功！服务器 \"{server_data['name']}\" 已添加到系统。"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="已取消添加服务器。"
                )
            
            # 清理用户状态
            del user_data[user_id]
        
        return True
    
    # 其他原有的消息处理逻辑
    if info["mode"] != "interactive":
        if info.get("operation") == "ping":
            await update.message.reply_text("命令式模式无需输入IP，如需重新测试，请使用 /ping。")
        elif info.get("operation") == "nexttrace":
            await update.message.reply_text("命令式模式无需输入IP，如需重新测试，请使用 /nexttrace。")
        return True

    if not info.get("target"):
        target = update.message.text.strip()
        info["target"] = target

        context.application.create_task(schedule_delete_message(context, update.message.chat_id, update.message.message_id, delay=5))

        if info.get("operation") == "ping":
            keyboard = [
                [
                    InlineKeyboardButton("Ping 5次", callback_data="nt_count_5"),
                    InlineKeyboardButton("Ping 10次", callback_data="nt_count_10"),
                    InlineKeyboardButton("Ping 30次", callback_data="nt_count_30")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.edit_message_text(
                chat_id=info["chat_id"],
                message_id=info["message_id"],
                text="请选择要 Ping 的次数：",
                reply_markup=reply_markup
            )
        elif info.get("operation") == "nexttrace":
            try:
                ipaddress.ip_address(target)
                trace_mode = info.get("trace_mode", "icmp")  # 默认为icmp
                await context.bot.edit_message_text(
                    chat_id=info["chat_id"],
                    message_id=info["message_id"],
                    text=f"目标： {target} 为IP地址，正在后台执行{('ICMP' if trace_mode == 'icmp' else 'TCP')}模式路由追踪操作，请稍候..."
                )
                context.application.create_task(
                    do_nexttrace_in_background(context, info["chat_id"], info["server_info"], target, "direct", user_id, trace_mode)
                )
            except ValueError:
                keyboard = [
                    [
                        InlineKeyboardButton("IPv4", callback_data="nt_iptype_ipv4"),
                        InlineKeyboardButton("IPv6", callback_data="nt_iptype_ipv6")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.edit_message_text(
                    chat_id=info["chat_id"],
                    message_id=info["message_id"],
                    text="请选择 IP 协议类型：",
                    reply_markup=reply_markup
                )
    else:
        await update.message.reply_text("你已输入过目标IP，如需重新测试，请使用相应的命令。")
    
    return True
