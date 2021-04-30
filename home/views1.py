from django.shortcuts import render,redirect
from home.models import User, user_activation, user_categories, user_profile, notifications, user_become
from teacher.models import categories, subcategories, Courses, Sections, VideoUploads
from student.models import student_register_courses,course_comments,student_cart_courses,student_favourite_courses, student_rating_courses
from teacher.views import getAllCourseList, get_courseDetails, getLanguage, getPaidCourseList, getFreeCourseList
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import json
import os, sys, shutil
import traceback
import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.conf import settings
import os, shutil
import datetime
from textblob import TextBlob
from django.core.wsgi import get_wsgi_application
import json
from django.conf.urls.static import static
from builtins import str as _str

import logging

# from moviepy.editor import VideoFileClip
import os
from django.core.mail import send_mail
import smtplib



os.environ['DJANGO_SETTINGS_MODULE'] = 'booctop.settings'
application = get_wsgi_application()

def home_view(request):

	course_list = getAllCourseList()
	course_free_list = getFreeCourseList()
	course_paid_list = getPaidCourseList()

	for course in course_list:
		rateList = course_comments.objects.filter(course_id_id=course.id).values_list('rating',flat=True)
		rateList = list(rateList)
		sum = 0;
		for i in rateList:
			sum += i
		cnt = len(rateList)
		if cnt == 0 :
			course.rating = 0
		else :
			course.rating = round(sum/cnt,1)
		course.video = getVideoCnt(course)
		course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
	for course in course_free_list:
		rateList = course_comments.objects.filter(course_id_id=course.id).values_list('rating', flat=True)
		rateList = list(rateList)
		sum = 0;
		for i in rateList:
			sum += i
		cnt = len(rateList)
		if cnt == 0:
			course.rating = 0
		else:
			course.rating = round(sum/cnt,1)
		course.video = getVideoCnt(course)
		course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
	for course in course_paid_list:
		rateList = course_comments.objects.filter(course_id_id=course.id).values_list('rating', flat=True)
		rateList = list(rateList)
		sum = 0;
		for i in rateList:
			sum += i
		cnt = len(rateList)
		if cnt == 0:
			course.rating = 0
		else:
			course.rating = round(sum/cnt,1)
		course.video = getVideoCnt(course)
		course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	category_obj = categories.objects.all()

	#show fav page.., cart page...
	favList = student_favourite_courses.objects.filter(student_id_id=request.user.id)
	favListShow = student_favourite_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartList = student_cart_courses.objects.filter(student_id_id=request.user.id)
	cartListShow = student_cart_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartTotalSum = 0

	#show notification...
	noti_list = notifications.objects.filter(user_id=user_id,is_read=0).order_by("-id")[:3]
	noti_cnt = notifications.objects.filter(user_id=user_id,is_read=0).count()

	for cart in cartList:
		cartTotalSum += cart.course_id.price
	if getLanguage(request)[1] == None:
		if user_type == "student":
			stu_courses = student_register_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:10]
			for course in stu_courses:
				courses = Courses.objects.get(pk=course.course_id_id)
				course.videoCnt = getVideoCnt(courses)
			print("stu_courses:::", stu_courses)
			return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"user_id":user_id,"category_obj":category_obj, 'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList),'stu_courses':stu_courses, 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
		else:
			if user_id:
				return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj,"user_id":user_id, 'favList':favListShow, 'cartList':cartListShow,  'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
			else:
				return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj, 'favList':favListShow, 'cartList':cartListShow,  'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
	else:
		ur=getLanguage(request)[1].split('/')
		if getLanguage(request)[0] =="":
			ln="en"
		else:
			ln="ar"
		if len(ur)==1 and ur[1]=="":
			la="en"
		else:
			la=ur[3]
		if la== ln:
			if user_type == "student":
				stu_courses = student_register_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:10]
				return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"user_id":user_id,"category_obj":category_obj,'favList':favListShow, 'cartList':cartListShow,'stu_courses':stu_courses, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
			else:
				if user_id:
					return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj,"user_id":user_id,'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
				else:
					return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj,'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
		else:
			li=getLanguage(request)[0].split('/')
			if len(ur)==7:
				u=ur[0]+"//"+ur[2]+"/"+ln+"/"+ur[4]+"/"+ur[5]+"/"
				
				if ur[5]=="":
					u=u[:len(u)-1]
					if user_type == "student":
						stu_courses = student_register_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:10]
						return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"user_id":user_id,"category_obj":category_obj,'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
					else:
						if user_id:
							return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj,"user_id":user_id,'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
						else:
							return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"category_obj":category_obj, 'favList':favListShow, 'cartList':cartListShow,'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
				else:
					return redirect(u)
			else:
				u=ur[0]+"//"+ur[2]+"/"+ln+"/"+ur[4]+"/"
				if ur[4]=="":
					u=u[:len(u)-1]
					if user_type == "student":
						return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],"user_id":user_id,'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
					else:
						if user_id:
							return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0],'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
						else:
							return render(request, 'index.html', {'course_list': course_list, 'course_free_list' : course_free_list, 'course_paid_list' : course_paid_list, 'lang': getLanguage(request)[0], 'favList':favListShow, 'cartList':cartListShow, "user_id":user_id, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})
				else:
					return redirect(u)

def signup(request):
	objC = categories.objects.all()
	return render(request, 'signup.html', {"objC":objC, 'lang': getLanguage(request)[0]})	 

def about(request):
	
	return render(request, 'about.html', {'lang': getLanguage(request)[0]})	 
   

def faqs(request):

	return render(request, 'faqs.html', {'lang': getLanguage(request)[0]})	

def help(request):

	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	
	return render(request, 'support.html', {'lang': getLanguage(request)[0],'user_type':user_type,"user_id":user_id})

def terms(request):

	return render(request, 'terms.html', {'lang': getLanguage(request)[0]})

def become(request):
	objC = categories.objects.all()
	return render(request, 'become.html', {'lang': getLanguage(request)[0], 'catList':objC})

# def single_course(request,id):
# 	user_type = request.session.get("user_type")
# 	user_id = request.session.get("user_id")
# 	course_id = request.GET.get('id')
# 	course = Courses.objects.get(id=id)
# 	data = get_courseDetails(id)

# 	if user_type == 'teacher':
# 		obj_comment = course_comments.objects.filter(course_id_id=id)
# 	else:
# 		obj_comment = course_comments.objects.filter(course_id_id=id).filter(user_id=user_id)
# 	list = []
# 	dict ={}
# 	print("testtest:",obj_comment, id)
# 	# show fav page.., cart page...
# 	favList = student_favourite_courses.objects.filter(student_id_id=request.user.id)
# 	favListShow = student_favourite_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
# 	cartList = student_cart_courses.objects.filter(student_id_id=request.user.id)
# 	cartListShow = student_cart_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
# 	cartTotalSum = 0

# 	# show notification...
# 	noti_list = notifications.objects.filter(user_id=request.user.id, is_read=0).order_by("-id")[:3]
# 	noti_cnt = notifications.objects.filter(user_id=request.user.id, is_read=0).count()

# 	teacher_id = Courses.objects.get(pk=id).user_id
# 	user_info = User.objects.get(pk=teacher_id)
# 	free_course = Courses.objects.filter(user_id=teacher_id).filter(type=1).count()
# 	paid_course = Courses.objects.filter(user_id=teacher_id).filter(type=0).count()

# 	rating_list = course_comments.objects.filter(course_id_id=course.id)

# 	includeList = Sections.objects.filter(course_id=id)
# 	course.rating = getRatingFunc(rating_list)

# 	for i in obj_comment:
# 		if User.objects.filter(id = i.user_id).exists():
# 			obj = User.objects.get(id = i.user_id)
			
# 			dict["user_name"] = obj.first_name+""+obj.last_name
# 			dict["user_img"] = obj.image
			
# 		dict["user_comment"] = i.comment
# 		dict["user_comment_id"] = i.id
# 		dict["course_id_id"] = i.course_id_id
# 		dict["date"] = i.date
		
# 		list.append(dict)
# 		dict ={}
# 	cur_course = Courses.objects.get(pk=id)
# 	is_me = 0
# 	if request.user.id == cur_course.user_id :
# 		is_me = 1

# 	first_list = []
# 	if Sections.objects.filter(course_id = id).exists():
# 		_obj = Sections.objects.filter(course_id=id, type="video")
# 		count = 0
# 		count_2 = 0
# 		for i in _obj:
# 			if VideoUploads.objects.filter(section_id=i.id).exists():
# 				eleDict = []
# 				video_obj = VideoUploads.objects.filter(section_id=i.id)
# 				for j in video_obj:
# 					myDict = {}
# 					count += 1
# 					myDict["sr_no"] = count
# 					myDict["url"] = j.url
# 					myDict["video_name"] = j.name
# 					eleDict.append(myDict)
# 				i.videoList = eleDict

# 			obj = Sections.objects.filter(course_id=id, type="video")
# 			count = 0
# 			count_2 = 0
# 			for i in obj:
# 				Dict = {}
# 				count += 1
# 				Dict["sr_no"] = count
# 				Dict["section_name"] = i.name
# 				id_course = i.course_id
# 				if VideoUploads.objects.filter(section_id=i.id).exists():
# 					video_obj = VideoUploads.objects.filter(section_id=i.id)
# 					for j in video_obj:
# 						Dict["url"] = j.url
# 						Dict["video_name"] = j.name
# 				if count < 2:
# 					first_list = Dict
# 					Dict = {}
# 				else:
# 					pass
# 	return render(request, 'single_course.html',{'question_list': data['question_list'], 'course': course,'user_type':user_type,"user_id":user_id,"course_list":list,'id':id, 'user_info':user_info, 'free_course':free_course,'paid_course':paid_course,'includeList':includeList, 'first_video':first_list, 'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list, 'is_me':is_me})

@csrf_exempt
def add_comment(request):

	course_id = request.POST.get("course_id")
	comment = request.POST.get("comment")
	# comment_id = request.POST.get("comment_id")
	rating = request.POST.get("rating")
	rating = float(rating)
	user_id = request.POST.get("user_id")
	dt = datetime.datetime.now()

	if course_comments.objects.filter(course_id_id=course_id,user_id=user_id).exists() :
		existRec = course_comments.objects.filter(course_id_id=course_id,user_id=user_id)[0]
		existRec.comment = comment
		existRec.rating = rating
		existRec.date = dt
		existRec.save()
	else :
		obj = course_comments(user_id = user_id,course_id_id = course_id,comment = comment,date = dt,rating=rating)
		obj.save()

	return HttpResponse("success")

def delete_comment(request):
	course_id = request.POST.get("id")
	obj = course_comments.objects.get(pk=course_id)
	print("delete",obj)
	obj.delete()
	return HttpResponse("success")

def ecommerce_cart(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'ecommerce_cart.html', {'lang': getLanguage(request)[0]})

def ecommerce_payment(request,id):
	if request.session.get('user_id') == None:
		return redirect('/')
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	course = Courses.objects.get(id=id)
	print(user_id)
	print(user_type)
	if user_type == "student":
		return render(request, 'ecommerce_payment.html', {'lang': getLanguage(request)[0] ,"course":course,"user_id":user_id })
	else:
		return redirect("/")

@csrf_exempt
def student_courses(request):
	student_id = request.POST.get('student')
	course_id = request.POST.get('course')

	txt = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	txt += '<html xmlns="http://www.w3.org/1999/xhtml">'
	txt += '<head>'
	txt += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="X-UA-Compatible" content="IE=edge">'
	txt += '<meta name="viewport" content="width=device-width, initial-scale=1">'
	txt += '<title>Thanks for purchase Course</title>'
	txt += '</head>'
	txt += '<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" bgcolor="#ffffff" style="margin-top: 0;margin-bottom: 0;padding-top: 0;padding-bottom: 0;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;-webkit-font-smoothing: antialiased;width: 100%;">'
	txt += '<div class="navbar-brand" style="float: unset;padding: unset;height: unset;"><h4 style="font-weight: 900">Hello ' + request.user.first_name + '! Congratlations! </h4></div>'
	txt += '</body>'
	txt += '</html>'

	to = request.user.email
	subject = 'Thanks for your purchasing.'

	msg = EmailMultiAlternatives(subject, '', '', [to])
	msg.attach_alternative(txt, "text/html")
	msg.send()
	
	if student_register_courses.objects.filter(student_id_id = student_id,course_id_id = course_id).exists():
		return HttpResponse("error")
	else:
		obj = student_register_courses(student_id_id = student_id,course_id_id = course_id)
		obj.save()
	
	return HttpResponse("success")

@csrf_exempt
def student_Cart_courses(request):
	student_id = request.POST.get('student')
	course_id = request.POST.get('course')

	if student_cart_courses.objects.filter(student_id_id = student_id,course_id_id = course_id).exists() == 0:
		obj = student_cart_courses(student_id_id = student_id,course_id_id = course_id)
		obj.save()
	return HttpResponse("success")

@csrf_exempt
def add_favourite_courses(request):
	student_id = request.POST.get('student')
	course_id = request.POST.get('course')
	if student_favourite_courses.objects.filter(course_id_id=course_id).exists() == 0 :
		obj = student_favourite_courses(student_id_id = student_id,course_id_id = course_id)
		obj.save()
	return HttpResponse("success")

def check_email(request):
	msg = ''
	try:
		
		email = request.POST.get('email')
		
		lstUsers = User.objects.filter(email=email)
		if len(lstUsers) > 0:
			msg = 'already'
		else:
			
			msg = 'success'
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n"	 + ": " + str(sys.exc_info())
	
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def getsubcategory(request):
	msg = ''
	try:
		category_id = request.POST.get('category_id')
		print("category id", category_id)
		subcat_list=[]
		objC = subcategories.objects.filter(categories_id=int(category_id))
		print("result subcategory", objC)
		for subcat in objC:
			item={'name' : subcat.name, 'image':subcat.image, 'category_name':subcat.categories.name, 'id':subcat.id }
			subcat_list.append(item)
		msg = 'success'
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n"	 + ": " + str(sys.exc_info())

	# to_return = {'msg': msg, 'subcat_list':subcat_list}
	to_return = {'msg': 'success', 'subcat_list':subcat_list}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def saveimg(request):
	msg = ''
	try:
		myfile = request.FILES['file']
		filename = myfile._get_name()

		ext = filename[filename.rfind('.'):]
		file_name = str(uuid.uuid4())+ext
		path = '/user_images/'
		full_path= str(path) + str(file_name)
		fd = open('%s/%s' % (settings.STATICFILES_DIRS[0],str(path) + str(file_name)), 'wb')
		for chunk in myfile.chunks():
			fd.write(chunk)
		fd.close()
		msg = 'success'
			


	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n"	 + ": " + str(sys.exc_info())
	
	#
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def register_user(request):
	msg = ''
	try:
		firstname = request.POST.get('first_name')
		lastname = request.POST.get('last_name')
		email = request.POST.get('email')
		password = request.POST.get('password')
		phone_number = request.POST.get('phone_number')
		subcategory_id = request.POST.get('subcategory')
		type = request.POST.get('type')
		group_id=1
		lstUsers = User.objects.filter(email=email)
		coun = User.objects.filter(email=email).count()
		if coun > 0:
			msg = 'already'
		else:
			try:
				myfile = request.FILES['file']
				filename = myfile._get_name()

				ext = filename[filename.rfind('.'):]
				file_name = str(uuid.uuid4())+ext
				path = '/user_images/'
				full_path= str(path) + str(file_name)
				fd = open('%s/%s' % (settings.STATICFILES_DIRS[0],str(path) + str(file_name)), 'wb')
				for chunk in myfile.chunks():
					fd.write(chunk)
				fd.close()
			except:
				full_path = '/assets/img/man.jpg'
			dt=datetime.datetime.now()
			objUser = User(email=email, first_name=firstname, last_name=lastname, phone_number=phone_number, password=password, is_staff=False,is_active=False,image=full_path, is_superuser=False,date_joined=dt)
			
			objUser.set_password(password)

			if type == "teacher":
				group_id=2
				
			if Group.objects.filter(id=group_id).exists():   
				group = Group.objects.get(id=group_id)
				
			else:
				group = Group(id=group_id)
				group.save()
				
			objUser.group = group
			objUser.save()
			objUA = user_activation()
			objUA.user = objUser
			objUA.code = str(uuid.uuid4())
			objUA.email = email
			objUA.save()
			user_group_id = str(objUser.group_id)
			
			if user_group_id == "1":
				request.session['user_id'] = str(objUser.id)
				request.session['user_type'] = "student"
			else:
				request.session['user_id'] = str(objUser.id)
				request.session['user_type'] = "teacher"

			if type == "teacher":
				# objSubCat = subcategories.objects.get(id=subcategory_id)
				objSubCat = subcategories.objects.get(id=subcategory_id)

				objUS = user_categories()
				objUS.user = objUser
				objUS.category = objSubCat
				objUS.save()
			domain = request.META['HTTP_HOST']
			msg = 'success'
			sendConfirmationMail(objUA, domain)
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n"	 ": " + str(sys.exc_info())
		
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

# Store updated profile in DB
def updateUserProfile(data):
	user_id = data.user.id
	bio = data.POST.get('acc_bio')
	cat_id = data.POST.get('cat_id')
	subcat_ids = data.POST.get('subcat_ids')
	facebook_url = data.POST.get('facebook_url')
	instagram_url = data.POST.get('instagram_url')
	twitter_url = data.POST.get('twitter_url')
	website_url = data.POST.get('website_url')
	is_notification = data.POST.get('is_notification')

	try:
		objProfile = user_profile.objects.get(user_id=user_id)
		objProfile.bio = bio
		objProfile.cat_id = cat_id
		objProfile.subcat_ids = subcat_ids
		objProfile.facebook_url = facebook_url
		objProfile.instagram_url = instagram_url
		objProfile.twitter_url = twitter_url
		objProfile.website_url = website_url
		objProfile.notification = is_notification
	except:	   
		objProfile = user_profile(
			user_id=user_id,
			bio=bio,
			cat_id=cat_id,
			subcat_ids=subcat_ids,
			facebook_url=facebook_url,
			instagram_url=instagram_url,
			twitter_url=twitter_url,
			website_url=website_url,
			notification=is_notification,			 
		)

	objProfile.save()

def update_user(request):
	msg = ''

	try:
		firstname = request.POST.get('first_name')
		lastname = request.POST.get('last_name')
		email = request.POST.get('email')
		objU = User.objects.get(email=email, id=request.user.id)

		# update user profile
		updateUserProfile(request)

		try:
			myfile = request.FILES['file']
			filename = myfile._get_name()
			ext = filename[filename.rfind('.'):]
			file_name = str(uuid.uuid4())+ext
			path = '/user_images/'
			full_path= str(path) + str(file_name)

			fd = open('%s/%s' % (settings.STATICFILES_DIRS[0],str(path) + str(file_name)), 'wb')
			for chunk in myfile.chunks():
				fd.write(chunk)
			fd.close()			  
		except:
			full_path = objU.image
		
		objU.first_name = firstname
		objU.last_name = lastname
		objU.image = full_path
		objU.save()
		
		msg = 'success'
			
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n"	 ": " + str(sys.exc_info())
		
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")


def sendConfirmationMail(objUA, domain):

	try:
		link = 'http://' + domain + '/activation?code=' + objUA.code
		txt = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
		txt += '<html xmlns="http://www.w3.org/1999/xhtml">'
		txt += '<head>'
		txt += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta http-equiv="X-UA-Compatible" content="IE=edge">'
		txt += '<meta name="viewport" content="width=device-width, initial-scale=1">'
		txt += '<title>Activation</title>'
		txt += '</head>'
		txt += '<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" bgcolor="#ffffff" style="margin-top: 0;margin-bottom: 0;padding-top: 0;padding-bottom: 0;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100%;-webkit-font-smoothing: antialiased;width: 100%;">'
		txt += '<div class="navbar-brand" style="float: unset;padding: unset;height: unset;"><h4 style="font-weight: 900">Hello '+ objUA.user.first_name +'</h4></div>'
		txt +=	"<a href='"+ link +"' > Click here </a> to activate your account"
		txt += '</body>'
		txt += '</html>'

		to = objUA.email

		subject = 'Thanks for activating your email, welcome!'
		msg = EmailMultiAlternatives(subject, '', '', [to])
		msg.attach_alternative(txt, "text/html")
		msg.send()
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n" + ": " + str(sys.exc_info())
		msg = tbinfo + "\n" + ": " + str(sys.exc_info())
		
def activation(request):
	cod = request.GET.get('code')
	lenobj = user_activation.objects.get(code=cod)
	lenobj.code = str(uuid.uuid4())
	lenobj.save()
	user_id = lenobj.user_id
	user_object = User.objects.get(id=user_id)

	user_object.is_active = True

	user_object.save()

	return HttpResponseRedirect("/")

def ajaxlogin(request):
	msg = ''
	try:
		email = request.POST.get('email')
		password = request.POST.get('password')
		remember = request.POST.get('remember')
		objU = authenticate(email=email, password=password)
		obj = User.objects.get(email = email)
		if objU is not None:
			if objU.is_active == True:
				login(request, objU)
				obj = User.objects.get(email = email)
				user_id = obj.id
				id = str(obj.group_id)

				if remember == 'true' :
					request.session['user_id'] = request.POST.get('email')
					request.session['password'] = request.POST.get('password')
					request.session['remember'] = request.POST.get('remember')

				if id == "1":
					request.session['user_id'] = str(user_id)
					request.session['user_type'] = "student"
				else:
					request.session['user_id'] = str(user_id)
					request.session['user_type'] = "teacher"
				request.session['password'] = request.POST.get('password')

				msg = 'success'
			else:
				msg = 'Not active'
		else:
			msg = 'error'
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n" +  ": " + str(sys.exc_info())
	
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def changepassword(request):
	msg = ''
	try:
		currentpassword = request.POST.get('currentpassword')
		print("currentpassword = ",currentpassword)
		newpassword = request.POST.get('newpassword')
		print("newpassword = ", newpassword)
		print("request.user.email = ",request.user.email)
		objU = authenticate(email=request.user.email, password=currentpassword)
		print(objU)
		if objU is not None:
			print("User is authenticated")
			u = User.objects.get(email=request.user.email)
			u.set_password(newpassword)
			u.save()
			msg = 'success'
		else:
			msg = 'error'
		print("msg - ",msg)
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n" +  ": " + str(sys.exc_info())
	#
	to_return = {'msg': msg}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def logout_(request):
	logout(request)
	return HttpResponseRedirect('/')


		
############# search engine
@csrf_exempt
def search_course(request): 
	print("search_course.................")
	cod = request.POST.get('inp')
	# course_list = getAllCourseList()
	course_list = []
	if cod=="":
		course_list = Courses.objects.all()
	else:	
		course_list = Courses.objects.filter(name__icontains=cod)
	cnt = Courses.objects.filter(name__icontains=cod).count()
	print("cnt",cnt)
	print("lang",getLanguage(request)[0],getLanguage(request)[1])
	
	if getLanguage(request)[1] == None:
		print("g")
		if getLanguage(request)[0] =="":
			ln="en"
		else:
			ln="ar"
		if len(ur)==1 and ur[1]=="":
			la="en"
		else:
			la=ur[3]
			
		if la== ln:
			if cnt>0:
				rendered = render_to_string('filter_course_list.html',{'course_list': course_list})
				return HttpResponse(rendered)
			else:
				rendered = render_to_string("filter_no_course.html",{"course":cod})
				return HttpResponse(rendered)
	else:
		print("jjjjjj",getLanguage(request)[1])
		ur=getLanguage(request)[1].split('/')
		print(ur)
		if getLanguage(request)[0] =="":
			ln="en"
		else:
			ln="ar"
		if len(ur)==1 and ur[1]=="":
			la="en"
		else:
			la=ur[3]
			
		if la== ln:
			for c in course_list:
				print("course_list",c.name,c.price)
			
			# rendered = render_to_string('filter_course_list.html',{'course_list': course_list})
				
			# return HttpResponse(rendered)
		else:
			print(getLanguage(request)[0].split('/'))
			li=getLanguage(request)[0].split('/')
			
			# if (li[0]=="" and len(li)==1) or (li[0]=="ar" and len(li)==2):
				# u=ur[0]+"//"+ur[2]+"/"+ln
			# else:
				# u=ur[0]+"//"+ur[2]+"/"+ln+"/"+ur[4]+"/"
			u=ur[0]+"//"+ur[2]+"/"+ln+"/"+ur[4]+"/"
			print("ur[4]",ur[4])
			if ur[4]=="":
				u=u[:len(u)-1]
				print(ur[4])
				print("course_list",course_list)
				# rendered = render_to_string('filter_course_list.html',{'course_list': course_list})
				# return HttpResponse(rendered)
			# else:
				# return redirect(u)
		if cnt>0:
			
			ul=ur[0]+"//"+ur[2]+"/"+ln+"/"
			print(getLanguage(request)[1],ul)
			
			
			# if getLanguage(request)[2] != ul:
				# print("he")
				#return render(request,'index.html',{'course_list': course_list, 'lang': getLanguage(request)[0]})
				#### return redirect('/')
			# else:	
				# print("hello")
				# if ur[4]=="":
			rendered = render_to_string('filter_course_list.html',{'course_list': course_list})
			return HttpResponse(rendered)
				# else:
					# return render(request,'index.html',{'course_list': course_list, 'lang': la})
					### return HttpResponse("success")
				
		else:
			
			rendered = render_to_string("filter_no_course.html",{"course":cod})
			return HttpResponse(rendered)
			
			
			
################## search engine 2
@csrf_exempt
def search_course2(request): 
	print("search_course2.................")
	cod = request.POST.get('inp')
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	if len(cod)>0:
		hi_blob = TextBlob(str(cod))
		if hi_blob.detect_language()=='ar':
			lang='ar'
			code=hi_blob.translate(to='en')
			print(code,type(code))	
		else:
			code=cod
			lang='en'
	else:
		code=""
		lang=getLanguage(request)[0]
	####################
	
	course_list = []
	if cod=="":
		course_list = Courses.objects.all()
	else:	
		course_list = Courses.objects.filter(name__icontains=code)
	cnt = Courses.objects.filter(name__icontains=code).count()
	print("cnt",cnt)
	print("lang",getLanguage(request)[0],getLanguage(request)[1])
	pat=getLanguage(request)[1].split('/')
	if pat[4]=="":
		if cnt>0:
			if user_type == "student":
				rendered = render_to_string('filter_course_list.html',{'course_list': course_list,"user_id":user_id})
				
			else:
				rendered = render_to_string('filter_course_list.html',{'course_list': course_list})
			
			return HttpResponse(rendered)
			
			
		else:
			if user_type == "student":
				rendered = render_to_string("filter_no_course.html",{"course":code,"user_id":user_id})
			
			else:
				rendered = render_to_string("filter_no_course.html",{"course":code})
				
			return HttpResponse(rendered)
	else:
		
		response={"status":"success","value":cod,"lang":lang}
		print("cod",cod)
		##############################
		print("type",type(cod))
		return JsonResponse(response)	
		
def getRatingFunc(rating_list):
	sum = 0
	count = 0
	for rate in rating_list:
		sum += rate.rating
		count += 1
	if count == 0:
		_rating = 0
	else:
		_rating = sum / count
	print("rating===>",round(_rating,1))
	return round(_rating,1)

def getVideoCnt(course):
	ssss = Sections.objects.filter(course_id=course.id).values_list("id", flat=True)
	ssss = map(str, ssss)
	strr = ','.join(ssss)
	videoListCnt = VideoUploads.objects.extra(where=['FIND_IN_SET(section_id, "' + strr + '")']).count()
	return videoListCnt

def getVideoList(course):
	ssss = Sections.objects.filter(course_id=course.id).values_list("id", flat=True)
	ssss = map(str, ssss)
	strr = ','.join(ssss)
	videoList = VideoUploads.objects.extra(where=['FIND_IN_SET(section_id, "' + strr + '")'])
	return videoList

@csrf_exempt
def sort_by_category(request):
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	category_id = request.POST.get("category_id")
	category_id_2 = request.POST.get("category_id_2")
	if category_id == '' :
		category_id = "All"
	if category_id_2 == '':
		category_id_2 = "All"

	if category_id_2 == "All":
		if category_id == "All":
			course_list = Courses.objects.all()
			course_free_list = Courses.objects.filter(type=1)
			course_paid_list = Courses.objects.filter(type=0)
			for course in course_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
			for course in course_free_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
			for course in course_paid_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
			if user_type == "student":
				rendered = render_to_string('filter_course_list.html', {'course_list': course_list, "user_id": user_id})
				rendered1 = render_to_string('filter_course_list.html',
											 {'course_list': course_free_list, "user_id": user_id})
				rendered2 = render_to_string('filter_course_list.html',
											 {'course_list': course_paid_list, "user_id": user_id})
			else:
				rendered = render_to_string('filter_course_list.html', {'course_list': course_list})
				rendered1 = render_to_string('filter_course_list.html', {'course_list': course_free_list})
				rendered2 = render_to_string('filter_course_list.html', {'course_list': course_paid_list})
			# return HttpResponse()
			return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		elif subcategories.objects.filter(categories_id=category_id).exists():
			sub_obj = subcategories.objects.filter(categories_id=category_id)
			for i in sub_obj:
				if Courses.objects.filter(scat_id=i.id).exists():
					obj_course = Courses.objects.filter(scat_id=i.id)
					obj_free_course = Courses.objects.filter(scat_id=i.id).filter(type=1)
					obj_paid_course = Courses.objects.filter(scat_id=i.id).filter(type=0)

					for course in obj_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					for course in obj_free_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					for course in obj_paid_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					if user_type == "student":
						rendered = render_to_string('filter_course_list.html',
													{'course_list': obj_course, "user_id": user_id})
						rendered1 = render_to_string('filter_course_list.html',
													 {'course_list': obj_free_course, "user_id": user_id})
						rendered2 = render_to_string('filter_course_list.html',
													 {'course_list': obj_paid_course, "user_id": user_id})
					else:
						rendered = render_to_string('filter_course_list.html', {'course_list': obj_course})
						rendered1 = render_to_string('filter_course_list.html', {'course_list': obj_free_course})
						rendered2 = render_to_string('filter_course_list.html', {'course_list': obj_paid_course})
				else:
					return HttpResponse("error")
				return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		else:
			return HttpResponse("error")
	elif category_id_2 == '1':
		if category_id == "All":
			course_list = Courses.objects.all()
			course_free_list = Courses.objects.filter(type=1)
			course_paid_list = Courses.objects.filter(type=0)

			max_rating_course = []
			max_rating_free_course = []
			max_rating_paid_course = []
			for course in course_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
			max_rating = 0

			for course in course_list:
				if course.rating >= 4.5:
					max_rating_course.append(course)

			for course in course_free_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()

			max_rating = 0
			for course in course_free_list:
				if course.rating >= 4.5:
					max_rating_free_course.append(course)

			for course in course_paid_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()

			max_rating = 0
			for course in course_paid_list:
				if course.rating >= 4.5:
					max_rating_paid_course.append(course)

			# course_list = []
			# course_free_list = []
			# course_paid_list = []
			# if max_rating_course != '':
			# 	course_list.append(max_rating_course)
			# if max_rating_free_course != '':
			# 	course_free_list.append(max_rating_free_course)
			# if max_rating_paid_course != '':
			# 	course_paid_list.append(max_rating_paid_course)

			if user_type == "student":
				rendered = render_to_string('filter_course_list.html', {'course_list': max_rating_course, "user_id": user_id})
				rendered1 = render_to_string('filter_course_list.html',
											 {'course_list': max_rating_free_course, "user_id": user_id})
				rendered2 = render_to_string('filter_course_list.html',
											 {'course_list': max_rating_paid_course, "user_id": user_id})
			else:
				rendered = render_to_string('filter_course_list.html', {'course_list': max_rating_course})
				rendered1 = render_to_string('filter_course_list.html', {'course_list': max_rating_free_course})
				rendered2 = render_to_string('filter_course_list.html', {'course_list': max_rating_paid_course})

			# return HttpResponse()
			return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})

		elif subcategories.objects.filter(categories_id=category_id).exists():
			sub_obj = subcategories.objects.filter(categories_id=category_id)
			for i in sub_obj:
				if Courses.objects.filter(scat_id=i.id).exists():
					obj_course = Courses.objects.filter(scat_id=i.id)
					obj_free_course = Courses.objects.filter(scat_id=i.id).filter(type=1)
					obj_paid_course = Courses.objects.filter(scat_id=i.id).filter(type=0)

					max_rating_course = ''
					max_rating_free_course = ''
					max_rating_paid_course = ''
					for course in obj_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					max_rating = 0
					for course in obj_course:
						if course.rating > max_rating:
							max_rating = course.rating
							max_rating_course = course

					for course in obj_free_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					max_rating = 0
					for course in obj_free_course:
						if course.rating > max_rating:
							max_rating = course.rating
							max_rating_free_course = course

					for course in obj_paid_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					max_rating = 0
					for course in obj_paid_course:
						if course.rating > max_rating:
							max_rating = course.rating
							max_rating_paid_course = course

					obj_course = []
					obj_free_course = []
					obj_paid_course = []

					if max_rating_course != '':
						obj_course.append(max_rating_course)
					if max_rating_free_course != '':
						obj_free_course.append(max_rating_free_course)

					if max_rating_paid_course != '':
						obj_paid_course.append(max_rating_paid_course)

					if user_type == "student":
						rendered = render_to_string('filter_course_list.html',
													{'course_list': obj_course, "user_id": user_id})
						rendered1 = render_to_string('filter_course_list.html',
													 {'course_list': obj_free_course, "user_id": user_id})
						rendered2 = render_to_string('filter_course_list.html',
													 {'course_list': obj_paid_course, "user_id": user_id})
					else:
						rendered = render_to_string('filter_course_list.html', {'course_list': obj_course})
						rendered1 = render_to_string('filter_course_list.html', {'course_list': obj_free_course})
						rendered2 = render_to_string('filter_course_list.html', {'course_list': obj_paid_course})
				else:
					return HttpResponse("error")
				return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		else:
			return HttpResponse("error")
	elif category_id_2 == '2':
		if category_id == "All":
			course_list = Courses.objects.all()
			course_free_list = Courses.objects.filter(type=1)
			course_paid_list = Courses.objects.filter(type=0)

			max_cnt_course = []
			max_cnt_free_course = []
			max_cnt_paid_course = []
			for course in course_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)
			max_cnt = 0
			for course in course_list:
				if course.stuCnt > max_cnt:
					max_cnt = course.stuCnt
					# max_cnt_course = course
			for course in course_list:
				if course.stuCnt == max_cnt:
					max_cnt_course.append(course)

			for course in course_free_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)

			max_cnt = 0
			for course in course_free_list:
				if course.stuCnt > max_cnt:
					max_cnt = course.stuCnt
					# max_cnt_free_course = course
			for course in course_free_list:
				if course.stuCnt == max_cnt:
					max_cnt_free_course.append(course)

			for course in course_paid_list:
				rating_list = course_comments.objects.filter(course_id_id=course.id)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course.rating = getRatingFunc(rating_list)
				course.video = getVideoCnt(course)

			max_cnt = 0
			for course in course_paid_list:
				if course.stuCnt > max_cnt:
					max_cnt = course.stuCnt
					# max_cnt_paid_course = course

			for course in course_paid_list:
				if course.stuCnt == max_cnt:
					max_cnt_paid_course.append(course)


			# course_list = []
			# course_free_list = []
			# course_paid_list = []
			# if max_cnt_course != '':
			# 	course_list.append(max_cnt_course)
			# if max_cnt_free_course != '':
			# 	course_free_list.append(max_cnt_free_course)
			#
			# if max_cnt_paid_course != '':
			# 	course_paid_list.append(max_cnt_paid_course)

			if user_type == "student":
				rendered = render_to_string('filter_course_list.html', {'course_list': max_cnt_course, "user_id": user_id})
				rendered1 = render_to_string('filter_course_list.html',
											 {'course_list': max_cnt_free_course, "user_id": user_id})
				rendered2 = render_to_string('filter_course_list.html',
											 {'course_list': max_cnt_paid_course, "user_id": user_id})
			else:
				rendered = render_to_string('filter_course_list.html', {'course_list': max_cnt_course})
				rendered1 = render_to_string('filter_course_list.html', {'course_list': max_cnt_free_course})
				rendered2 = render_to_string('filter_course_list.html', {'course_list': max_cnt_paid_course})

			# return HttpResponse()
			return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})

		elif subcategories.objects.filter(categories_id=category_id).exists():
			sub_obj = subcategories.objects.filter(categories_id=category_id)
			for i in sub_obj:
				if Courses.objects.filter(scat_id=i.id).exists():
					obj_course = Courses.objects.filter(scat_id=i.id)
					obj_free_course = Courses.objects.filter(scat_id=i.id).filter(type=1)
					obj_paid_course = Courses.objects.filter(scat_id=i.id).filter(type=0)

					max_cnt_course = ''
					max_cnt_free_course = ''
					max_cnt_paid_course = ''
					for course in obj_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
					max_cnt = 0
					for course in obj_course:
						if course.stuCnt > max_cnt:
							max_cnt = course.stuCnt
							max_cnt_course = course

					for course in obj_free_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
					max_cnt = 0
					for course in obj_free_course:
						if course.stuCnt > max_cnt:
							max_cnt = course.stuCnt
							max_cnt_free_course = course

					for course in obj_paid_course:
						rating_list = course_comments.objects.filter(course_id_id=course.id)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						course.rating = getRatingFunc(rating_list)
						course.video = getVideoCnt(course)
					max_cnt = 0
					for course in obj_paid_course:
						if course.stuCnt > max_cnt:
							max_cnt = course.stuCnt
							max_cnt_paid_course = course

					obj_course = []
					obj_free_course = []
					obj_paid_course = []
					if max_cnt_course != '':
						obj_course.append(max_cnt_course)
					if max_cnt_free_course != '':
						obj_free_course.append(max_cnt_free_course)
					if max_cnt_paid_course != '':
						obj_paid_course.append(max_cnt_paid_course)

					if user_type == "student":
						rendered = render_to_string('filter_course_list.html',
													{'course_list': obj_course, "user_id": user_id})
						rendered1 = render_to_string('filter_course_list.html',
													 {'course_list': obj_free_course, "user_id": user_id})
						rendered2 = render_to_string('filter_course_list.html',
													 {'course_list': obj_paid_course, "user_id": user_id})
					else:
						rendered = render_to_string('filter_course_list.html', {'course_list': obj_course})
						rendered1 = render_to_string('filter_course_list.html', {'course_list': obj_free_course})
						rendered2 = render_to_string('filter_course_list.html', {'course_list': obj_paid_course})
				else:
					return HttpResponse("error")
				return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		else:
			return HttpResponse("error")
	elif category_id_2 == '3':
		if category_id == "All":
			course_list = Courses.objects.all().order_by('-created_at')
			course_free_list = Courses.objects.filter(type=1).order_by('-created_at')
			course_paid_list = Courses.objects.filter(type=0).order_by('-created_at')
			if len(course_list) > 0:
				course = course_list[0]
				ratingList = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(ratingList)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course_list = []
				course_list.append(course)
			else :
				course_list = []

			if len(course_free_list) > 0:
				course = course_free_list[0]
				ratingList = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(ratingList)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course_free_list = []
				course_free_list.append(course)

			else :
				course_free_list = []

			if len(course_paid_list) > 0:
				course = course_paid_list[0]
				ratingList = course_comments.objects.filter(course_id_id=course.id)
				course.rating = getRatingFunc(ratingList)
				course.video = getVideoCnt(course)
				course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
				course_paid_list = []
				course_paid_list.append(course)
			else :
				course_paid_list = []

			if user_type == "student":
				rendered = render_to_string('filter_course_list.html', {'course_list': course_list, "user_id": user_id})
				rendered1 = render_to_string('filter_course_list.html',
											 {'course_list': course_free_list, "user_id": user_id})
				rendered2 = render_to_string('filter_course_list.html',
											 {'course_list': course_paid_list, "user_id": user_id})
			else:
				rendered = render_to_string('filter_course_list.html', {'course_list': course_list})
				rendered1 = render_to_string('filter_course_list.html', {'course_list': course_free_list})
				rendered2 = render_to_string('filter_course_list.html', {'course_list': course_paid_list})

			# return HttpResponse()
			return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		elif subcategories.objects.filter(categories_id=category_id).exists():
			sub_obj = subcategories.objects.filter(categories_id=category_id)
			for i in sub_obj:
				if Courses.objects.filter(scat_id=i.id).exists():
					obj_course = Courses.objects.filter(scat_id=i.id).order_by('-created_at')
					obj_free_course = Courses.objects.filter(scat_id=i.id).filter(type=1).order_by('-created_at')
					obj_paid_course = Courses.objects.filter(scat_id=i.id).filter(type=0).order_by('-created_at')

					if len(obj_course) > 0:
						course = obj_course[0]
						ratingList = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(ratingList)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						obj_course = []
						obj_course.append(course)
					else :
						obj_course = []

					if len(obj_free_course) > 0:
						course = obj_free_course[0]
						ratingList = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(ratingList)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						obj_free_course = []
						obj_free_course.append(course)
					else :
						obj_free_course = []

					if len(obj_paid_course) > 0:
						course = obj_paid_course[0]
						ratingList = course_comments.objects.filter(course_id_id=course.id)
						course.rating = getRatingFunc(ratingList)
						course.video = getVideoCnt(course)
						course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
						obj_paid_course = []
						obj_paid_course.append(course)
					else :
						obj_paid_course = []

					if user_type == "student":
						rendered = render_to_string('filter_course_list.html',
													{'course_list': obj_course, "user_id": user_id})
						rendered1 = render_to_string('filter_course_list.html',
													 {'course_list': obj_free_course, "user_id": user_id})
						rendered2 = render_to_string('filter_course_list.html',
													 {'course_list': obj_paid_course, "user_id": user_id})
					else:
						rendered = render_to_string('filter_course_list.html', {'course_list': obj_course})
						rendered1 = render_to_string('filter_course_list.html', {'course_list': obj_free_course})
						rendered2 = render_to_string('filter_course_list.html', {'course_list': obj_paid_course})
				else:
					return HttpResponse("error")
				return JsonResponse({"rendered": rendered, "rendered1": rendered1, "rendered2": rendered2})
		else:
			return HttpResponse("error")

def becomeTeacher(request):
	id = request.POST.get('id')
	cat_id = request.POST.get('cat_id')
	sub_catid = request.POST.get('sub_catid')

	if user_become.objects.filter(user_id=id).exists() :
		one = user_become.objects.filter(user_id=id)[0]
		one.cat_id = cat_id
		one.sub_catid = sub_catid
		one.save()

	else :
		one = user_become(
			user_id=id,
			cat_id=cat_id,
			sub_catid=sub_catid
		)
		one.save()
	ret = {'msg':'success'}
	return JsonResponse(ret)

def single_category(request,id):
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	if id == '1':
		categorie = "Web Development"
	
	elif id == '2':
		categorie = "Business"
	
	elif id == '3':
		categorie = "Aviation"
	
	elif id == '4':
		categorie = "Games"
	
	elif id =='5':
		categorie = "Mathmatics"	
	
	elif id == '6':
		categorie = "Life style"	
	
	elif id == '7':
		categorie = "Arts"
	
	elif id == '8':
		categorie = "Information Technology"
	
	elif id == '9':
		categorie = "Drama & Cinema"
	
	elif id == '10':
		categorie = "software Programming"
	
	elif id == '11':
		categorie = "Languages"
	
	elif id == '12':
		categorie = "Food & Cooking"
	
	elif id == '13':
		categorie = "Repare & Maintaince"
	
	elif id == '14':
		categorie = "Skills"
	
	else:
		categorie = "All"

	category = ''
	if categories.objects.filter(name = categorie).exists():
		category_id = categories.objects.get(name = categorie).id
		category = categories.objects.get(name = categorie)
	else:
		return render(request,'filter_404_page.html', {'lang': getLanguage(request)[0]})
	if getLanguage(request)[1] == None:
		l=""
	else:	
		ur=getLanguage(request)[1].split('/')
		l=ur[3]
	
		if l=="ar":
			l="ar/"
		else:
			l=""
	
	if categorie == "All":
		course_list = Courses.objects.all()
		count = course_list.count()

		if l !=getLanguage(request)[0]:
			rl=getLanguage(request)[1].split('/')
			return render(request, 'single_category.html', {'lang': getLanguage(request)[0],'course_list':course_list,"course_cnt":str(count),'category':category})
			
		else:
			rl=getLanguage(request)[1].split('/')
			return render(request, 'single_category.html', {'lang': getLanguage(request)[0],'course_list':course_list,"course_cnt":str(count),"user_id":user_id,'category':category})

	elif subcategories.objects.filter(categories_id = category_id).exists():
		sub_obj = subcategories.objects.filter(categories_id = category_id)
		for i in sub_obj:
			if Courses.objects.filter(scat_id = i.id).exists():

				course_list = Courses.objects.filter(scat_id = i.id)
				course_free_list = Courses.objects.filter(scat_id=i.id, type=1)
				course_paid_list = Courses.objects.filter(scat_id=i.id, type=0)

				for course in course_list:
					rating_list = course_comments.objects.filter(course_id_id=course.id)
					course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					course.rating = getRatingFunc(rating_list)
					course.video = getVideoCnt(course)

				for course in course_free_list:
					rating_list = course_comments.objects.filter(course_id_id=course.id)
					course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					course.rating = getRatingFunc(rating_list)
					course.video = getVideoCnt(course)

				for course in course_paid_list:
					rating_list = course_comments.objects.filter(course_id_id=course.id)
					course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
					course.rating = getRatingFunc(rating_list)
					course.video = getVideoCnt(course)

				count = course_list.count()

				if l !=getLanguage(request)[0]:
					rl=getLanguage(request)[1].split('/')
					return render(request, 'single_category.html', {'lang': getLanguage(request)[0],'course_list':course_list,"course_cnt":str(count),"course_name":categorie,"user_id":user_id,'category':category,'course_free_list':course_free_list,'course_paid_list':course_paid_list})
						
				else:
					return render(request, 'single_category.html', {'lang': getLanguage(request)[0],'course_list':course_list,"course_cnt":str(count),"course_name":categorie,"user_id":user_id,'category':category,'course_free_list':course_free_list,'course_paid_list':course_paid_list})
			
			else:
				return render(request,'filter_404_page.html', {'lang': getLanguage(request)[0]})
	else:
		return render(request,'filter_404_page.html', {'lang': getLanguage(request)[0]})


##add by me...

def getPromoData(request):
	course_id = request.POST.get('course_id')
	course = Courses.objects.get(pk=course_id)
	rateList = course_comments.objects.filter(course_id_id=course_id)
	cnt=0
	sum=0
	for rate in rateList:
		sum += rate.rating
		cnt += 1
	if cnt == 0:
		rating = 0
	else :
		rating = sum / cnt
	course.rating = rating
	ssss = Sections.objects.filter(course_id=course.id).values_list("id", flat=True)
	ssss = list(ssss)

	promoVideo = []
	for s in ssss:
		if VideoUploads.objects.filter(section_id=s).filter(promo=1).exists():
			videos = VideoUploads.objects.filter(section_id=s).filter(promo=1)
			for video in videos:
				promoVideo.append(video)
	if len(promoVideo) > 0:
		curVideo = promoVideo[0].url
	else:
		curVideo = ''
	course.curVideo = curVideo
	course.video = promoVideo
	user = User.objects.get(pk=course.user_id)
	course.user = user

	myUserList = student_register_courses.objects.filter(course_id_id=course.id)
	permit = 0
	for one in myUserList:
		if request.user.id == one.student_id_id :
			permit = 1
			pass
	print("permit",permit)
	print("video",course.video)
	print("curVideo",course.curVideo)
	lender = render_to_string('video_modal.html',{'course':course,'user':request.user,'permit':permit})
	return JsonResponse({"lender":lender, "msg":"success"})

def showCartList(request):
	if request.session.get('user_id') == None:
		return redirect('/')

	user_id = request.user.id
	cartList = student_cart_courses.objects.filter(student_id_id=user_id)

	# show fav page.., cart page...
	favList = student_favourite_courses.objects.filter(student_id_id=request.user.id)
	favListShow = student_favourite_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartList = student_cart_courses.objects.filter(student_id_id=request.user.id)
	cartListShow = student_cart_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartTotalSum = 0

	# show notification...
	noti_list = notifications.objects.filter(user_id=request.user.id, is_read=0).order_by("-id")[:3]
	noti_cnt = notifications.objects.filter(user_id=request.user.id, is_read=0).count()

	return render(request, 'cart.html',{'cartList':cartList, 'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})

def showFavList(request):
	if request.session.get('user_id') == None:
		return redirect('/')

	# show fav page.., cart page...
	favList = student_favourite_courses.objects.filter(student_id_id=request.user.id)
	favListShow = student_favourite_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartList = student_cart_courses.objects.filter(student_id_id=request.user.id)
	cartListShow = student_cart_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartTotalSum = 0

	# show notification...
	noti_list = notifications.objects.filter(user_id=request.user.id, is_read=0).order_by("-id")[:3]
	noti_cnt = notifications.objects.filter(user_id=request.user.id, is_read=0).count()

	user_id = request.user.id
	favList = student_favourite_courses.objects.filter(student_id_id=user_id)
	for fav in favList:
		course = Courses.objects.get(pk=fav.course_id_id)
		fav.videoCnt = getVideoCnt(course)
		fav.stuCnt = student_register_courses.objects.filter(course_id_id=fav.course_id_id).count()
	return render(request, 'wishlist.html', {'favList':favList, 'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})

def saveNotification(request):
	user = request.POST.get('user')
	text = request.POST.get('text')
	sender = request.POST.get('sender')
	one = notifications(
		user_id=user,
		text=text,
		sender_id=sender
	)
	one.save()
	ret = {'msg':'success'}
	return JsonResponse(ret)

def viewProfile(request,id):
	# users = User.objects.exclude(group_id=1)
	user = User.objects.get(pk=id)

	# show fav page.., cart page...
	favList = student_favourite_courses.objects.filter(student_id_id=request.user.id)
	favListShow = student_favourite_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartList = student_cart_courses.objects.filter(student_id_id=request.user.id)
	cartListShow = student_cart_courses.objects.filter(student_id_id=request.user.id).order_by("-id")[:3]
	cartTotalSum = 0

	# show notification...
	noti_list = notifications.objects.filter(user_id=request.user.id, is_read=0).order_by("-id")[:3]
	noti_cnt = notifications.objects.filter(user_id=request.user.id, is_read=0).count()

	if user_profile.objects.filter(user_id=id).exists():
		profile = user_profile.objects.filter(user_id=id)[0]
		catIds = profile.subcat_ids
		subCatStr1 = subcategories.objects.extra(where=["find_in_set(id,'"+catIds+"')"]).values_list('name',flat=True)
		subCatStr1 = map(str, subCatStr1)
		subCatStr = ','.join(subCatStr1)
		profile.subCatStr = subCatStr
		user.profile = profile
		courses = Courses.objects.filter(user_id=id)
		for course in courses:
			rating_list = course_comments.objects.filter(course_id_id=course.id)
			course.rating = getRatingFunc(rating_list)
		user.courses = courses
		coursesID = Courses.objects.filter(user_id=id).values_list('id',flat=True)
		courseIDStr = map(str, coursesID)
		mystr = ','.join(courseIDStr)
		review = course_comments.objects.extra(where=["find_in_set(course_id_id,'"+mystr+"')"])
		user.review = review
		user.reviewCnt = len(review)
	return render(request, 'profile.html',{'teacher':user, 'favList':favListShow, 'cartList':cartListShow, 'favCnt':len(favList),'cartCnt':len(cartList), 'cartTotalSum':cartTotalSum, 'noti_cnt':noti_cnt, 'noti_list':noti_list})

def teacherProfile(request):
	id = request.POST.get('id')
	user = User.objects.get(pk=id)
	if user_profile.objects.filter(user_id=id).exists():
		profile = user_profile.objects.filter(user_id=id)[0]
		user.profile = profile
	return render(request,'teacherProfile.html',{'user':user})

def deleteAccount(request):
	user_id = request.POST.get('id')

	User.objects.get(pk=user_id).delete()

	return JsonResponse({'msg':'success'})

def deleteCourse(request):
	course_id = request.POST.get("id")
	Courses.objects.get(pk=course_id).delete()
	return JsonResponse({'msg':'success'})

def handler404(request, exception):
	return render(request, 'filter_404_page.html')