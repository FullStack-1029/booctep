# from django.urls import path
from django.conf.urls import include, url, i18n
from teacher.views import *
from student.views import *

urlpatterns = [

    url(r'^store-course/$', store_course, name="store course"),
    url(r'^store-course-2/$', store_course_2, name="store course2"),
    url(r'^store-course-3/$', store_course_3, name="store course3"),

    url(r'^get-coursedetails/$', getCourseDetailsById, name="get course details"),
   
    url(r'^video_check/$', video_check, name="video_check"),
    url(r'^savePaymentInfo/$', savePaymentInfo, name='get certificate'),
]