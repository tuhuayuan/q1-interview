# pyright: reportUndefinedVariable=false

class HttpRequest:
    # 假定一个request类型
    def __init__(self, body={}):
        self.body = body

def score_or_zero(s):
    try:
        return int(s)
    except Exception:
        return 0

def add_score_endpoint(request):
    # 确定request对象类型，避免过多的判断检测
    if not isinstance(request, HttpRequest):
        raise ValueError('Invalid request')

    # 必选参数检测
    if 'user_id' not in request.body or 'score' not in request.body:
        raise ValueError('Missing required parameters') 
    
    # 持久化加载
    repo = get_repo()
    if repo is None:
        raise ValueError('Repository connection failed')
    
    user = repo.get_user(user_id)
    if user is None:
        raise ValueError(f'User {user_id} not found')
    
    score = score_or_zero(request.body['score'])
    
    # 业务逻辑判断
    if user.has_role('staff'):
        user.score += score
    elif user.has_role('admin'):
        user.score += score * score_or_zero(request.body['score_modifier'])

    user.last_login = datetime.now()

    try:
        # 写入业务
        repo.update_user(user)
    except Exception as e:
        raise ValueError(f'Failed to update user: {e}')

    return {'user_id': user.user_id, 'score': user.score}
