"""
数据库模型定义（8 张表）
小区物业管理系统 - 数据库课程大作业
表结构:
  1. User     - 统一用户表（管理员/员工/业主）
  2. Owner    - 业主详情表
  3. House    - 房屋表
  4. Fee      - 物业费表
  5. Repair   - 报修表
  6. Complaint- 投诉建议表
  7. Visitor  - 访客表
  8. Notice   - 公告表
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


# ==================== 1. 用户表（统一认证） ====================
class User(models.Model):
    """统一用户表，role 区分管理员/员工/业主"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('staff', '物业员工'),
        ('owner', '业主'),
    ]
    username = models.CharField('用户名', max_length=50, unique=True)
    password = models.CharField('密码', max_length=128)
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES)
    name = models.CharField('姓名', max_length=50)
    phone = models.CharField('电话', max_length=20, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def set_password(self, raw_password):
        """密码哈希存储"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """验证密码"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.name}({self.get_role_display()})'


# ==================== 2. 业主详情表 ====================
class Owner(models.Model):
    """业主扩展信息，与 User 一对一关联"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账号')
    gender = models.CharField('性别', max_length=2, choices=[('男', '男'), ('女', '女')])
    id_card = models.CharField('身份证号', max_length=18, unique=True)
    address = models.CharField('联系地址', max_length=200, blank=True, default='')

    class Meta:
        db_table = 'owner'
        verbose_name = '业主'
        verbose_name_plural = '业主'

    def __str__(self):
        return self.user.name


# ==================== 3. 房屋表 ====================
class House(models.Model):
    """房屋信息，一个房屋只能绑定一个业主"""
    STATUS_CHOICES = [
        ('occupied', '已入住'),
        ('vacant', '空置'),
        ('renovating', '装修中'),
    ]
    owner = models.OneToOneField(
        Owner, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='业主', unique=True
    )
    building = models.CharField('楼栋', max_length=20)
    unit = models.CharField('单元', max_length=10)
    room = models.CharField('房号', max_length=10)
    area = models.DecimalField('面积(m²)', max_digits=8, decimal_places=2)
    layout = models.CharField('户型', max_length=20)
    status = models.CharField('状态', max_length=15, choices=STATUS_CHOICES, default='vacant')

    class Meta:
        db_table = 'house'
        verbose_name = '房屋'
        verbose_name_plural = '房屋'
        unique_together = [('building', 'unit', 'room')]

    @property
    def full_address(self):
        return f'{self.building}栋{self.unit}单元{self.room}室'

    def __str__(self):
        return self.full_address


# ==================== 4. 物业费表 ====================
class Fee(models.Model):
    """物业费账单"""
    STATUS_CHOICES = [
        (0, '未缴'),
        (1, '已缴'),
    ]
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='房屋')
    amount = models.DecimalField('金额(元)', max_digits=10, decimal_places=2)
    month = models.CharField('费用月份', max_length=7, help_text='格式: 2026-05')
    status = models.IntegerField('缴费状态', choices=STATUS_CHOICES, default=0)
    pay_time = models.DateTimeField('缴费时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'fee'
        verbose_name = '物业费'
        verbose_name_plural = '物业费'
        unique_together = [('house', 'month')]

    def __str__(self):
        return f'{self.house} - {self.month} - {self.amount}元'


# ==================== 5. 报修表 ====================
class Repair(models.Model):
    """业主报修工单"""
    STATUS_CHOICES = [
        (0, '待处理'),
        (1, '处理中'),
        (2, '已完成'),
    ]
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='报修业主')
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='报修房屋')
    content = models.TextField('报修内容')
    submit_time = models.DateTimeField('提交时间', auto_now_add=True)
    status = models.IntegerField('处理状态', choices=STATUS_CHOICES, default=0)
    staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='处理员工', limit_choices_to={'role': 'staff'}
    )
    process_time = models.DateTimeField('处理时间', null=True, blank=True)
    result = models.TextField('处理结果', blank=True, default='')

    class Meta:
        db_table = 'repair'
        verbose_name = '报修'
        verbose_name_plural = '报修'

    def __str__(self):
        return f'{self.owner.user.name} - {self.content[:20]}'


# ==================== 6. 投诉建议表 ====================
class Complaint(models.Model):
    """业主投诉与建议"""
    STATUS_CHOICES = [
        (0, '待处理'),
        (1, '已回复'),
    ]
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='投诉业主')
    content = models.TextField('投诉/建议内容')
    submit_time = models.DateTimeField('提交时间', auto_now_add=True)
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    reply = models.TextField('回复内容', blank=True, default='')
    reply_time = models.DateTimeField('回复时间', null=True, blank=True)

    class Meta:
        db_table = 'complaint'
        verbose_name = '投诉建议'
        verbose_name_plural = '投诉建议'

    def __str__(self):
        return f'{self.owner.user.name} - {self.content[:20]}'


# ==================== 7. 访客表 ====================
class Visitor(models.Model):
    """访客登记记录"""
    name = models.CharField('访客姓名', max_length=50)
    phone = models.CharField('访客电话', max_length=20)
    reason = models.CharField('来访事由', max_length=200, default='探访')
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='拜访房屋')
    visit_time = models.DateTimeField('来访时间', default=timezone.now)
    staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='登记员工', limit_choices_to={'role': 'staff'}
    )

    class Meta:
        db_table = 'visitor'
        verbose_name = '访客'
        verbose_name_plural = '访客'

    def __str__(self):
        return self.name


# ==================== 8. 公告表 ====================
class Notice(models.Model):
    """物业公告"""
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发布人')
    publish_time = models.DateTimeField('发布时间', auto_now_add=True)
    is_public = models.BooleanField('业主可见', default=True)

    class Meta:
        db_table = 'notice'
        verbose_name = '公告'
        verbose_name_plural = '公告'

    def __str__(self):
        return self.title
