# pyright: reportUndefinedVariable=false

def add_score_endpoint(request):
    # request可能为None，且类型错误比如不包含body属性å
    # 以下假设request的类型是正确的
    if 'user_id' in request.body:
        # 1、repo可能为None，或者获取连接的时候出现异常
        # 2、get_repo如果每个请求都创建了一个新的连接，可能会导致耗尽服务器资源
        repo = get_repo()
        user = repo.get_user(request.body['user_id'])
        if user is not None:
            # 下方代码两个'score' in request.body是必选参数，应该在方法顶部检查并保证类型安全
            if user.has_role('staff'):
                if 'score' in request.body:
                    # score参数的类型需要安全转换
                    user.score += request.body['score']
                    user.last_login = datetime.now()
                    repo.update_user(user)
                    return user.dict()
            elif user.has_role('admin'):
                if 'score' in request.body:
                    if 'score_modifier' in request.body:
                        # score_modifier参数的类型需要安全转换
                        user.score += request.body['score'] * request.body['score_modifier']
                        user.last_login = datetime.now()
                        repo.update_user(user)
                        return user.dict()   
            else:
                # else里面对于user存在的情况下是通用的逻辑
                # repo.update_user需要检测可能的异常或返回值
                user.last_login = datetime.now()
                repo.update_user(user)
                return user.dict()
            
    # 直接返回dict可能导致数据泄漏
    # 如果框架能把异常转换为对应的HTTP响应那这样是OK的
    raise ValueError('Invalid request')