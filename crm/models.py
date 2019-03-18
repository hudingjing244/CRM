from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    name=models.CharField(max_length=32,blank=True,null=True)
    qq=models.CharField(max_length=64,unique=True)
    phone=models.CharField(max_length=64,blank=True,null=True)
    email = models.EmailField(max_length=64,blank=True,null=True)
    source_choices=((0,"转介绍"),
                    (1, "官网"),
                    (2, "百度推广"),
                    (3, "知乎"),
                    (4, "市场部推广"),
                    (5, "qq群"),
                    )
    source=models.SmallIntegerField(choices=source_choices)
    referral_from=models.CharField(verbose_name="转介绍人QQ",max_length=64,blank=True,null=True)

    consult_course=models.ForeignKey("Course",verbose_name="咨询课程",on_delete=models.CASCADE)
    content=models.TextField(verbose_name="咨询详情")
    tags=models.ManyToManyField('Tag',blank=True,null=True)
    consultant=models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    memo=models.TextField(blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)  # 表示对象创建时间,也就是记录创建时间

    def __str__(self):
        return self.qq
    class Meta:
        verbose_name='客户信息'
        verbose_name_plural='客户信息'

class Tag(models.Model):
    name=models.CharField(unique=True,max_length=32)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='标签'
        verbose_name_plural='标签'

class CustomerFollowUp(models.Model):
    '''客户跟进表'''
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE)
    content=models.TextField(verbose_name='跟进内容')
    consultant=models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    intention_choices=((0,'两周内报名'),
                       (1, '1月内报名'),
                       (2, '近期无报名计划'),
                       (3, '确定不会报名'),
                       (4, '已报名'),
                       (5,'犹豫不决'),
                       )
    intention=models.SmallIntegerField(choices=intention_choices)

    def __str__(self):
        return "<%s : %s>"%(self.customer.qq,self.intention)
    class Meta:
        verbose_name='客户跟进表'
        verbose_name_plural='客户跟进表'

class Branch(models.Model):
    '''校区'''
    name=models.CharField(max_length=64,unique=True)
    addr=models.CharField(max_length=128)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='校区信息'
        verbose_name_plural='校区信息'

class Course(models.Model):
    '''课程表'''
    name=models.CharField(max_length=64,unique=True)
    price=models.PositiveIntegerField()
    period=models.PositiveIntegerField(verbose_name="课程时长（月）")
    outline=models.TextField()

    def __str__(self):
        return self.name
    class Meta:
        verbose_name='课程表'
        verbose_name_plural='课程表'

class ClassList(models.Model):
    '''班级表'''
    branch=models.ForeignKey("Branch",on_delete=models.CASCADE)
    course=models.ForeignKey('Course',on_delete=models.CASCADE)
    semester=models.PositiveIntegerField(verbose_name="学期")
    teachers=models.ManyToManyField("UserProfile")
    class_type_choices=((0,"面授（脱产）"),
                        (1,"面授（周末）"),
                        (2,"网络班"),
                        )
    class_type=models.SmallIntegerField(verbose_name="上课方式",choices=class_type_choices)
    start_data=models.DateField(verbose_name="开班日期")

    class Meta:
        unique_together=("branch","course","semester")#三者都有不是唯一，但是其组合必须唯一
        verbose_name = '班级信息'
        verbose_name_plural = '班级信息'

    def __str__(self):
        return "%s %s %s"%(self.branch,self.course,self.semester)

class CourseRecord(models.Model):
    '''上课记录'''
    from_class=models.ForeignKey("ClassList",on_delete=models.CASCADE)
    day_num=models.PositiveSmallIntegerField(verbose_name="第几日")
    teacher=models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    has_homework=models.BooleanField(default=True)
    homework_title=models.CharField(max_length=128,blank=True,null=True)
    homework_content=models.TextField(verbose_name="作业内容",blank=True,null=True)
    outline=models.TextField(verbose_name="本节课程大纲")

    class Meta:
        unique_together=("from_class","day_num")
        verbose_name = '上课记录'
        verbose_name_plural = '上课记录'

    def __str__(self):
        return "%s %s"%(self.from_class,self.day_num)

class StudyRecord(models.Model):
    '''学习记录'''
    student=models.ForeignKey("Enrollment",on_delete=models.CASCADE)
    course_record=models.ForeignKey("CourseRecord",on_delete=models.CASCADE)
    attendance_choices=(
        (0,'已签到'),
        (1, '迟到'),
        (2, '缺勤'),
        (3, '早退'),
    )
    attendance=models.SmallIntegerField(choices=attendance_choices,default=0)
    score_choices=(
        (100, 'A+'),
        (90, 'A'),
        (85, 'B+'),
        (80, 'B'),
        (75, 'B-'),
        (65, 'C+'),
        (60, 'C'),
        (40, 'C-'),
        (-50,"D"),
        (-100, 'COPY'),
        (0, 'N/A'),#not avaliable
    )
    score=models.SmallIntegerField(choices=score_choices)
    memo=models.TextField(blank=True,null=True)
    date=models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = '学生成绩'
        verbose_name_plural = '学生成绩'

    def __str__(self):
        return "%s %s %s"%(self.student,self.course_record,self.score)

class Enrollment(models.Model):
    '''报名表'''
    customer=models.ForeignKey("Customer",on_delete=models.CASCADE)
    enrolled_class=models.ForeignKey("ClassList",verbose_name="所报班级",on_delete=models.CASCADE)
    consultant=models.ForeignKey("UserProfile",verbose_name="课程顾问",on_delete=models.CASCADE)
    contract_agreed=models.BooleanField(default=False,verbose_name="学生已同意条款")
    contract_approved=models.BooleanField(default=False,verbose_name="合同审核通过")
    time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.customer,self.enrolled_class)

    class Meta:
        unique_together=("customer","enrolled_class")
        verbose_name = '报名信息'
        verbose_name_plural = '报名信息'

class Payment(models.Model):
    '''缴费表'''
    customer=models.ForeignKey("Customer",on_delete=models.CASCADE)
    courses=models.ForeignKey("Course",on_delete=models.CASCADE)
    amount=models.PositiveIntegerField(default=500)
    consultant=models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.customer,self.amount)

    class Meta:
        verbose_name = '缴费信息'
        verbose_name_plural = '缴费信息'

class UserProfile(models.Model):
    '''账户表'''
    user=models.OneToOneField(User,on_delete=models.CASCADE)#ForeignKey是oneToMany,User是Django自己的表
    name=models.CharField(max_length=32)
    roles=models.ManyToManyField("Role",blank=True,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '账户信息'
        verbose_name_plural = '账户信息'


class Role(models.Model):
    '''角色表'''
    name=models.CharField(max_length=32,unique=True)
    def __str___(self):
        return  "%s"%(self.name)
    class Meta:
        verbose_name = '职位'
        verbose_name_plural = '职位'