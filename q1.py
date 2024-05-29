def add_score_endpoint(request):
    if 'user_id' in request.body:
        repo = get_repo()
        user = repo.get_user(request.body['user_id'])
        if user is not None:
            if user.has_role('staff'):
                if 'score' in request.body:
                    user.score += request.body['score']
                    user.last_login = datetime.now()
                    repo.update_user(user)
                    return user.dict()
            elif user.has_role('admin'):
                if 'score' in request.body:
                    if 'score_modifier' in request.body:
                        user.score += request.body['score'] * request.body['score_modifier']
                        user.last_login = datetime.now()
                        repo.update_user(user)
                        return user.dict()
            else:
                user.last_login = datetime.now()
                repo.update_user(user)
                return user.dict()

    raise ValueError('Invalid request')