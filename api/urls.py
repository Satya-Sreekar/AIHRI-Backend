from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_text, name='generate_text'),
    path('models/', views.list_models, name='list_models'),
    path('tts/', views.text_to_speech, name='text_to_speech'),
    path('tts/test/', views.test_tts, name='test_tts'),
] 