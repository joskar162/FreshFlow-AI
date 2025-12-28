from django.urls import path
from .views import TrainModelsView, RecommendView

urlpatterns = [
    path('train/', TrainModelsView.as_view(), name='train_models'),
    path('recommend/<str:customer_id>/', RecommendView.as_view(), name='recommend'),
]