from api.models import Article
from api.serializers import ArticleSerializer
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view
from django.http import JsonResponse
from api.forms import SignupForm
import json
from django.contrib.auth.models import User

@api_view(['POST'])
def signup(request) :
    if request.method == 'POST' :
        form = SignupForm(request.POST)
        print(request.POST)
        if form.is_valid() :
            user = form.save(commit=False)
            if User.objects.filter(email=user.email).exists():
                return JsonResponse({'account_created':False})
            user.save()#add user
            return JsonResponse({'account_created':True})
        else :
            return JsonResponse({'account_created':False})

@api_view(['GET'])
def user_profile(request) :
    if request.user.is_authenticated :
        profile={"username":request.user.username, "email":request.user.email}
        return Response(profile, status=status.HTTP_200_OK)
    return Response('', status=status.HTTP_401_UNAUTHORIZED)

class ArticleList(APIView) :
    def get(self, request, format=None):
        if request.user.is_authenticated :
            articles = Article.objects.filter(writer=request.user).values()
            return Response(articles, status=status.HTTP_200_OK)
        return Response('', status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, format=None) :
        if request.user.is_authenticated :
            serializer = ArticleSerializer(data=request.data)
            if serializer.is_valid() :
                serializer.save(writer=request.user)
                jsonString = {}
                jsonString['id'] = int(serializer.data['id'])
                return HttpResponse(json.dumps(jsonString), content_type="application/json", status=status.HTTP_201_CREATED) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("",status=status.HTTP_400_BAD_REQUEST)
class ArticleDetail(APIView) :
    def get_object(self, pk) :
        try :
            return Article.objects.get(id=pk)
        except Article.DoesNotExist :
            raise Http404
    
    def get(self, request, pk, format=None) :
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        if str(getattr(article, 'writer')) == request.user.username :#인증
            return Response(serializer.data)
        else :
            return Response("This is not your article.", status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, formoat=None) :
        article = self.get_object(pk)
        serializer = ArticleSerializer(article, data=request.data)
        if str(getattr(article, 'writer')) == request.user.username :#인증
            if serializer.is_valid() :
                serializer.save()
                return Response(serializer.data)
        else :
            return Response("This is not your article.", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None) :
        article = self.get_object(pk)
        if str(getattr(article, 'writer')) == request.user.username :#인증
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return Response("This is not your article.", status=status.HTTP_400_BAD_REQUEST)
#api