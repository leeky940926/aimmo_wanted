import json

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, F

from postings.models  import (
    Category, 
    Posting
)
from users.models     import User
from users.utils      import login_decorator

class PostingView(View) :
    @login_decorator
    def post(self, request) :
        try :
            data = json.loads(request.body)

            user     = request.user
            category = Category.objects.get(id=data['category'])
            
            Posting.objects.create(
                category    = category,
                user        = user,
                title       = data['title'],
                content     = data['content']
            )

            return JsonResponse({'message' : 'Posting Success'}, status=201)

        except KeyError :
            return JsonResponse({'message' : 'Key Error'}, status=400)

        except Category.DoesNotExist :
            return JsonResponse({'message' : 'Category matching query does not exist'}, status=400)
        
    def get(self, request) :
        try :
            keyword = request.GET.get('keyword', None)

            q = Q()

            q.add(Q(title__icontains=keyword), q.AND)
            q.add(Q(content__icontains=keyword), q.OR)

            posting_list = [{
                'id'         : posting.id,
                'title'      : posting.title,
                'content'    : posting.content,
                'created_at' : posting.created_at,
                'name'       : User.objects.get(id=posting.user_id).name,
                'user_id'    : User.objects.get(id=posting.user_id).id
            }for posting in Posting.objects.filter(q)]

            return JsonResponse({'posting_list':posting_list}, status=200)
        
        except ValueError :
            return JsonResponse({'message' : 'Value Error'}, status=400)

class PostingParamView(View) :
    def get(self, request, posting_id) :
        try : 
            user_id = request.session.get('user', None)

            posting = Posting.objects.get(id = posting_id)

            posting_list = [{
                'id'          : posting.id,
                'title'       : posting.title,
                'content'     : posting.content,
                'writer_id'   : posting.user_id,
                'writer_name' : User.objects.get(id=posting.user_id).name
            }]

            if not user_id :

                posting.views += 1
                posting.save()

                return JsonResponse({'message' : 'Success and increase views', 'posting_list' : posting_list}, status=200)
            
            return JsonResponse({'message' : 'Success but not increase views', 'posting_list' : posting_list}, status=200)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'})

    @login_decorator
    def post(self, request, posting_id) :
        try :
            data = json.loads(request.body)
            
            posting = Posting.objects.get(id=posting_id)

            title    = data.get('title',    posting.title)
            content  = data.get('content',  posting.content)
            category = data.get('category', posting.category_id)

            Posting.objects.filter(id=posting_id).update(
                title    = title,
                content  = content,
                category = category
            )

            return JsonResponse({'message' : 'Update Success'}, status=201)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'}, status=400)

    @login_decorator
    def delete(self, request, posting_id) :
        try :
            posting = Posting.objects.get(id=posting_id)
            posting.delete()
            return JsonResponse({'message' : 'Delete Success'}, status=201)
        
        except Posting.DoesNotExist :
            return JsonResponse({'message' : 'Posting matching query does not exist'}, status=400)