from django.shortcuts import render,redirect
from teacher.models import categories, Courses, VideoUploads, Sections, questions, student_mark, answers
from home.models import User, user_profile, notifications
from student.models import student_register_courses, student_rating_courses, course_comments
from datetime import datetime
import os, sys, shutil
import traceback
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
import uuid
from django.conf import settings


def teacher_account(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	objC = categories.objects.all()
	profile = user_profile.objects.get(user_id=request.user.id)

	return render(request, 'teacher/account.html', {'objC':objC, 'profile':profile, 'lang': getLanguage(request)[0]})

def teacher_security(request):

	if request.session.get('user_id') == None:
		return redirect('/')
	user_id = request.session.get('user_id')
	password = request.session.get('password')
	print("passwrod", password)
	print("user_id", user_id)
	return render(request, 'teacher/security.html', {'lang': getLanguage(request)[0], 'user_id': user_id, 'password': password})

def teacher_notifications(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	id = request.user.id
	noti_list = notifications.objects.filter(user_id=id,is_read=0)

	for noti in noti_list:
		noti.is_read = 1
		noti.save()

	course_list = Courses.objects.filter(user_id=id)
	course_id = Courses.objects.filter(user_id=id).values_list('id',flat=True)
	ids = map(str, course_id)
	_ids = ','.join(ids)
	student_list = student_register_courses.objects.extra(where=['FIND_IN_SET(course_id_id, "' + _ids + '")'])
	print("stude:",student_list)
	return render(request, 'teacher/notifications.html', {'lang': getLanguage(request)[0],'noti_list':noti_list, 'course_list':course_list,'student_list':student_list})
	
def teacher_payments(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/payments.html', {'lang': getLanguage(request)[0]})

def teacher_privacy(request):
	return render(request, 'teacher/privacy.html', {'lang': getLanguage(request)[0], 'user_id':request.user.id})

def dashboard(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	user_id = request.session.get('user_id')
	courses = Courses.objects.filter(user_id=user_id).filter(type=0)

	#price logic..
	totalPrice = 0
	#get total student
	courseId = Courses.objects.filter(user_id=user_id).values_list('id',flat=True)
	courseId = list(courseId)
	courseId = map(str, courseId)
	courseId = ','.join(courseId)
	totalStuCnt = student_register_courses.objects.extra(where=['FIND_IN_SET(course_id_id, "'+courseId+'")']).count()

	#get total rating
	rateSum = 0
	rateCnt = 0
	for course in courses:
		rating = course_comments.objects.filter(course_id_id=course.id).values_list('rating',flat=True)
		rating = list(rating)
		sum = 0;
		for i in rating:
			sum += i
		if len(rating) == 0:
			course.rating = 0
		else :
			course.rating = sum / len(rating)
		course.stuCnt = student_register_courses.objects.filter(course_id_id=course.id).count()
		course.totalGain = course.price*course.stuCnt
		totalPrice += course.totalGain
		rateSum += course.rating
		rateCnt += 1
	if rateCnt == 0:
		totalRate = 0
	else :
		totalRate = round(rateSum/rateCnt,2)
	return render(request, 'teacher/dashboard.html', {'lang': getLanguage(request)[0],'courses':courses, 'totalRate':totalRate, 'totalStuCnt':totalStuCnt,'totalPrice':totalPrice})

def teacher_courses(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	filter_type = request.GET.get('filter_type')
	if filter_type == None:
		filter_type = '-1'
	if int(filter_type) == -1:
		course_list = get_teacher_CourseList(request)
		filter_type = -1
	else:
		user_id = request.session.get("user_id")
		course_list = Courses.objects.filter(user_id=user_id,type=filter_type)
		filter_type = int(filter_type)

	return render(request, 'teacher/courses.html', {'lang': getLanguage(request)[0], 'course_list': course_list, 'user_type':request.session.get('user_type'),'filter_type':filter_type})

def teacher_faqs(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/faqs.html', {'lang': getLanguage(request)[0]}) 

def course_engagement(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	cur_course_id = request.GET.get('course_id')

	courses = get_teacher_CourseList(request)
	if cur_course_id == None:
		if len(courses) > 0:
			cur_course_id = courses[0].id
		else :
			cur_course_id = 0

	if len(courses) > 0:
		course = Courses.objects.get(pk=cur_course_id)
		# total price...

		# total students
		count = student_register_courses.objects.filter(course_id_id=course.id).count()
		course.stuCnt = count

		# total rating
		rateList = course_comments.objects.filter(course_id_id=course.id).values_list('rating', flat=True)
		rateList = list(rateList)
		sum = 0
		for i in rateList:
			sum += i
		if len(rateList) == 0:
			course.rating = 0
		else:
			course.rating = sum / len(rateList)

		#reviews...
		reviewList = course_comments.objects.filter(course_id_id=cur_course_id)

	else:
		course = ''
		reviewList = ''
	return render(request, 'teacher/course-engagement.html', {'lang': getLanguage(request)[0],'courses':courses, 'course':course, 'reviewList':reviewList, 'cur_course_id':cur_course_id})

def student_performance(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	user_id = request.user.id
	course_id = request.POST.get('course_id')
	courseList = Courses.objects.filter(user_id=user_id).order_by("id")
	if len(courseList) > 0:
		if course_id == None:
			course_id = courseList[0].id
		# get all course that i made..
		studentList = student_mark.objects.filter(course_id=course_id)
		for student in studentList:
			student.user = User.objects.get(pk=student.student_id)
			student.percent = student.mark * 20
			student.count = answers.objects.filter(student_id=student.student_id,result=1).count()

	else :
		course_id = ''
	return render(request, 'teacher/student-performance.html', {'lang': getLanguage(request)[0],'courseList':courseList, 'course_id':course_id*1, 'studentList':studentList})
	
def teacher_messages(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	if user_id :
		
		profile = User.objects.get(id = user_id)
		
		user_name = profile.first_name+" "+profile.last_name 
	
	student_list= []
	student_dict= {}
	
	if Courses.objects.filter(user_id = user_id).exists():
			
		obj = Courses.objects.filter(user_id = user_id)
			
		for i in obj:
				
			if student_register_courses.objects.filter(course_id = i.id).exists():
				
				student_dict["course_name"] = i.name
				student_dict["course_id"] = i.id
				
				student_obj = student_register_courses.objects.filter(course_id = i.id)
				
				for k in student_obj:
					
					student_dict["student_id"] = k.student_id.id
					student_dict["student_name"] = k.student_id.first_name+" "+k.student_id.last_name 
					student_dict["student_image"] = k.student_id.image
		
					student_list.append(student_dict)	
					student_dict = {}			
	
	
		return render(request, 'teacher/messages.html', {'lang': getLanguage(request)[0], 'datetime':datetime,"student_list":student_list,"user_id":user_id,"user_name":user_name})	 
	
	else:
		
		return render(request, 'teacher/messages.html', {'lang': getLanguage(request)[0], 'datetime':datetime,"user_id":user_id})

def dashboard1(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/dashboard_1.html', {'lang': getLanguage(request)[0]})	 

def guideline(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/guidline.html', {'lang': getLanguage(request)[0]})	  
	
def teacher_help(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/help.html', {'lang': getLanguage(request)[0]})	  

def help2(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/help2.html', {'lang': getLanguage(request)[0]})	   

def newcourse2(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	if request.method == 'POST':
		course = request.POST.get('course')
	else :
		course = ''
	return render(request, 'teacher/new-course-2.html', {'lang': getLanguage(request)[0], 'course_id': course})

def newcourse3(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	if request.method == 'POST':
		course = request.POST.get('course')
	else :
		course = ''
	return render(request, 'teacher/new-course-3.html', {'lang': getLanguage(request)[0], 'course_id':course})

def newcourse4(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	id = request.GET.get('id')
	data = get_courseDetails(id)
	course = Courses.objects.get(pk=id)
	include = course.includes
	incList = include.split(',')
	incList.pop()
	videoList = getVideoList(course)

	if len(videoList) > 0:
		showVideoUrl = videoList[0].url
	else :
		showVideoUrl = ''
	return render(request, 'teacher/new-course-4.html', {'lang': getLanguage(request)[0], 'video_list': data['video_list'], 'question_list': data['question_list'], 'section_list': data['section_list'],'course':course,'incList':incList, 'video_url':showVideoUrl})

def newcourse5(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/new-course-5.html', {'lang': getLanguage(request)[0]})	  

def newcourse(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	course = []
	obj_cat = categories.objects.all()
	autoUrl = ''
	if request.method == 'POST':
		course_id = request.POST.get('course')
		course = Courses.objects.get(pk=course_id)
		descript = course.includes.split(",")
		descript.pop()
		course.includes = descript
	else :
		course_id = ''
	courseCnt = Courses.objects.filter(user_id=request.user.id).count()
	teacher_name = request.user.first_name + " " + request.user.last_name
	courseNo = ''
	idx = (courseCnt + 1)
	while idx < 1000 :
		idx = idx * 10
		courseNo += '0'
	autoUrl = teacher_name + "_" + courseNo + str(courseCnt + 1)

	return render(request, 'teacher/new-course.html', {'lang': getLanguage(request)[0], 'categories':obj_cat, 'autoUrl':autoUrl, 'course':course, 'course_id':course_id})

def nocourseengagement(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/no-course-engagement.html', {'lang': getLanguage(request)[0]})	  

def nocourse(request):
	if request.session.get('user_id') == None:
		return redirect('/')
	return render(request, 'teacher/no-course.html', {'lang': getLanguage(request)[0]})

# post

# get all course list
# @return List

def get_teacher_CourseList(request):
	user_id = request.session.get("user_id")
	user_type = request.session.get("user_type")
	
	print(user_id)
	print(user_type)
	
	course_list = []
	course_list = Courses.objects.filter(user_id = user_id) 
	return course_list


def getAllCourseList():
	course_list = []
	course_list = Courses.objects.all()
	return course_list

def getPaidCourseList():
	course_list = []
	course_list = Courses.objects.filter(type=0)
	return course_list

def getFreeCourseList():
	course_list = []
	course_list = Courses.objects.filter(type=1)
	return course_list

# store course in DB
def store_course(request):

	id = request.POST.get('id')
	name = request.POST.get('name')
	description = request.POST.get('description')
	requirements = request.POST.get('requirements')
	gains = request.POST.get('gains')
	include = request.POST.get('include')
	category_id = request.POST.get('category_id')
	sub_category_id = request.POST.get('sub_category_id')
	price = request.POST.get('price')
	courseUrl = request.POST.get('courseUrl')
	user_id = request.POST.get('user_id')
	pending = request.POST.get('pending')
	type = request.POST.get('type')

	myfile = request.FILES['coverImg']
	filename = myfile._get_name()
	ext = filename[filename.rfind('.'):]
	file_name = str(uuid.uuid4()) + ext
	path = '/user_images/'
	full_path = str(path) + str(file_name)

	fd = open('%s/%s' % (settings.STATICFILES_DIRS[0], str(path) + str(file_name)), 'wb')
	for chunk in myfile.chunks():
		fd.write(chunk)
	fd.close()

	if id == '': # add case
		objCourse = Courses(
			name = name,
			description = description,
			requirements = requirements,
			gains = gains,
			includes = include,
			scat_id = category_id,
			price = price,
			user_id=request.user.id,
			cover_img=full_path,
			course_url=courseUrl,
			pending = pending,
			type = type
		)
		objCourse.save()
		print('success')
		msg = "successs"
		id = objCourse.id
	else :
		objCourse = Courses.objects.get(pk=id)
		objCourse.name = name
		objCourse.description = description
		objCourse.requirements = requirements
		objCourse.gains = gains
		objCourse.includes = include
		objCourse.scat_id = category_id
		objCourse.price = price
		objCourse.user_id = request.user.id
		objCourse.cover_img = full_path
		objCourse.course_url = courseUrl
		objCourse.pending = pending
		objCourse.type = type
		objCourse.save()
		msg = "successs"
		id = objCourse.id

	to_return = {
		'msg': msg,
		'id': id}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

# store videos in DB
def store_course_2(request):
	data = request.POST
	course_id = json.loads(data.get("course_id"))
	pending = json.loads(data.get("pending"))
	files = request.FILES
	video_list = []
	msg = ''

	course = Courses.objects.get(pk=course_id)
	course.pending = pending
	course.save()

	try:
		section_list = data.get("section_list")
		section_list = json.loads(section_list)
		json_video_list = json.loads(data.get("video_list"))	  

		if( len(json_video_list) > 0 ):
			## store section in DB
			for section in section_list:
				name = section['name']
				tag_id = section['tag_id']

				## store section in DB
				objSection = Sections(
					name=name,
					course_id=course_id,
					type='video',
					nos=tag_id
				)
				objSection.save()
				section_id = objSection.id
				for item in json_video_list:
					if( item['sectionId'] == tag_id ) :
						## upload video
						video_key = item['key']
						video = files[video_key]
						
						filename = video._get_name()
						ext = filename[filename.rfind('.'):]
						file_name = str(uuid.uuid4())+ext
						path = '/uploads/courses/videos/'
						full_path= str(path) + str(file_name)
						fd = open('%s/%s' % (settings.STATICFILES_DIRS[0],str(path) + str(file_name)), 'wb')	  
						for chunk in video.chunks():
							fd.write(chunk)
						fd.close()

						## store video in DB
						objVideo = VideoUploads(
							name=filename,
							section_id=section_id,
							url=full_path,
						)
						objVideo.save()
			msg = "success"
		else:
			msg = "failed"
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n" +  ": " + str(sys.exc_info())
	to_return = {
		'msg': msg,
	}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

# store questions in DB
def store_course_3(request):
	msg = ''
	data = request.POST
	course_id = json.loads(data.get("course_id"))
	try:
		question_list = json.loads(data.get('question_list'))
		section_list = json.loads(data.get('section_list'))
		key = 1  # question number
		if( len(question_list) > 0 ) :
			for section in section_list:
				tag_id = section['tag_id']
				section_name = section['name']
				nos = Sections.objects.filter(course_id=course_id).count()
				## store section in DB
				objSection = Sections(
					name=section_name,
					course_id=course_id,
					type='question',
					nos=nos+1
				)
				objSection.save()
				section_id = objSection.id

				for question in question_list:
					if question['section_id'] == tag_id :
						title = question['question_title']
						type = question['answer_type']
						answers = question['answers']

						content = ''
						result = ''
						for answer in answers:
							content += answer['data']
							content += ','
						# if type != 'aw-dragula':
						# 	for answer in answers:
							result += answer['result']
							result += ','

						objQuestion = questions(
							title=title,
							section_id=section_id,
							type=type,
							content=content,
							answer=result,
							nos=key
						)

						objQuestion.save()
						key += 1
			msg = "success"
		else :
			msg = "failed"
	except:
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]
		msg = tbinfo + "\n" +  ": " + str(sys.exc_info())
	to_return = {
		'msg': msg,
	}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

# get course details by course's id.
#
# @param Request
#
# @return HttpResponse
def getCourseDetailsById(request):
	id = request.POST.get('id')
	msg = ''
	to_return = {
		'msg': msg,
		'data': get_courseDetails(id)
	}
	serialized = json.dumps(to_return)
	return HttpResponse(serialized, content_type="application/json")

def get_courseDetails(course_id):
	id = course_id
	video_list = []
	question_list = []
	section_list = []
	tmp_sections = Sections.objects.filter(course_id=id)

	if len(tmp_sections) > 0:
		for section in tmp_sections:
			section_list.append({
				'id': section.id,
				'name': section.name,
				'course_id': section.course_id,
				'type': section.type,
			})
			for video in VideoUploads.objects.filter(section_id=section.id):
				video_list.append({
					'id': video.id,
					'name': video.name,
					'section_id': video.section_id,
					'src': video.url,
				})
			for question in questions.objects.filter(section_id=section.id):
				question_list.append({
					'id': question.id,
					'title': question.title,
					'type': question.type,
					'section_id': question.section_id,
					'nos': question.nos,
					'content': question.content,
					'answer': question.answer,
				})
	print(section_list)
	return {
		'question_list': question_list,
		'video_list': video_list,
		'section_list': section_list,
	}
ur=""
# language=""
def getLanguage(request):
	global ur;
	# global language;
	# prev=""
	path = request.path
	ur=path
	prev=request.META.get('HTTP_REFERER')
	# print(prev.split('/'))
	############################
	# if prev == None:
		# language = path.split('/')[1]
	# else:
		# p=prev.split('/')
		# if "en" in p:
			# language="en"
		# if "ar"	in p:
			# language="ar"
	######################	
	language = path.split('/')[1]

	if language == "ar":
		language = language + '/'
	else:
		language = ""
	# language = ""
	# print(path)
	# print("path...",path)
	# print("language...",language)
	# print("prev...",prev)
	# print("path...",path)
	return language,prev,path
	
def saveLater(request):
	id = request.POST.get('id')
	pending = request.POST.get('pending')
	print(id,pending)
	course = Courses.objects.get(pk=id)
	print(course)
	course.pending = pending
	course.save()

	ret = {'msg': 'success'}

	return JsonResponse(ret)

def getVideoList(course):
	ssss = Sections.objects.filter(course_id=course.id).values_list("id", flat=True)
	ssss = map(str, ssss)
	strr = ','.join(ssss)
	videoList = VideoUploads.objects.extra(where=['FIND_IN_SET(section_id, "' + strr + '")'])
	return videoList

	