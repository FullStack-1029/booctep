# from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url, i18n
# from home.views import saveimg, getsubcategory, changepassword, update_user, register_user, ajaxlogin, check_email, getPromoData, deleteAccount
from home.views import *
from video.views import *
from teacher.views import *


#POSTS
urlpatterns = [
    url(r'^login/$', ajaxlogin, name='login'),
    url(r'^register-user', register_user, name='register'),
    url(r'^update-user', update_user, name='update'),       
    url(r'^check-email', check_email, name='check email'),    
    url(r'^saveimg/$', saveimg, name='saveimg'),
    url(r'^getsubcategory$', getsubcategory, name='getsubcategory'),
    url(r'^changepassword/$', changepassword, name='changepassword'),
    url(r'^search_course/$', search_course, name='search_course'),
    url(r'^search_course2/$', search_course2, name='search_course2'),
	url(r'^student_courses/$', student_courses, name='student_courses'),
    
	url(r'^student_Cart_courses/$', student_Cart_courses, name='student_Cart_courses'),
    url(r'^delete_Cart_course_single/$', delete_Cart_course_single, name='delete_Cart_course_single'),
    url(r'^delete_Cart_courses_all/$', delete_Cart_courses_all, name='delete Cart courses all'),

	url(r'^student_favourite_courses/$', student_Favourite_courses, name='student_favourite_courses'),
    url(r'^delete_favourite_course_single/$', delete_Favourite_course_single, name='delete_Favourite_course_single'),
    url(r'^delete_favourite_courses_all/$', delete_Favourite_courses_all, name='delete Favourite courses all'),

	url(r'^sort_by_category/$', sort_by_category, name='sort_by_category'),
	url(r'^add_comment/$', add_comment, name='add_comment'),
	url(r'^delete_comment/$', delete_comment, name='add_comment'),
    url(r'^student-performance/$', student_performance, name='teacher student-performance'),

    #add mesingle_category
    url(r'^getPromoData/$', getPromoData, name='get promo data'),
    url(r'^deleteAccount/$', deleteAccount, name='delete account'),
    url(r'^deleteCourse/$', deleteCourse, name='delete a course'),

    url(r'^saveQuizAnswer/$', saveQuizAnswer, name='delete a course'),
    url(r'^saveQuizMark/$', saveQuizMark, name='get mark to a student'),

    url(r'^getCertificate/$', getCertificate, name='get certificate'),

    url(r'^saveNotification/$', saveNotification, name='save notifications'),

    url(r'^viewProfile/(?P<id>[0-9]+)/$', viewProfile, name='save notifications'),
    url(r'^teacherProfile/$', teacherProfile, name='show teacher profile '),
    url(r'^becomeTeacher/$', becomeTeacher, name='show teacher profile '),

# VIDEOS
    url(r'^video/playground/(?P<id>[0-9]+)/$', playground, name='video playground'),
    url(r'^video/playground/(?P<id>[0-9]+)/addtoprogress/$', addtoprogress, name='video addtoprogress'),

    url(r'^video/quiz/(?P<id>[0-9]+)/$', video_quiz, name='video quiz'),
    url(r'^video/quiz2/$', video_quiz2, name='teacher quiz2'),
    # url(r'^video/quiz2/(?P<id>[0-9]+)/$', video_quiz2, name='teacher quiz2'),
    url(r'^video/quiz3/(?P<id>[0-9]+)/$', video_quiz3, name='teacher quiz3'),


]