"""表单验证"""
from django import forms
from .models import User, Owner, House, Fee, Repair, Complaint, Visitor, Notice


class LoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField(label='用户名', max_length=50,
                               widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    password = forms.CharField(label='密码', max_length=128,
                               widget=forms.PasswordInput(attrs={'placeholder': '请输入密码'}))
    role = forms.ChoiceField(label='角色', choices=[('admin', '管理员'), ('staff', '员工'), ('owner', '业主')])


class UserForm(forms.ModelForm):
    """用户表单（管理员创建员工/业主账号）"""
    confirm_password = forms.CharField(label='确认密码', max_length=128,
                                       widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'name', 'phone']
        widgets = {
            'password': forms.PasswordInput(),
            'username': forms.TextInput(attrs={'placeholder': '登录用户名'}),
            'name': forms.TextInput(attrs={'placeholder': '真实姓名'}),
            'phone': forms.TextInput(attrs={'placeholder': '手机号码'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('两次密码输入不一致')
        return cleaned


class OwnerForm(forms.ModelForm):
    """业主信息表单"""
    class Meta:
        model = Owner
        fields = ['gender', 'id_card', 'address']
        widgets = {
            'id_card': forms.TextInput(attrs={'placeholder': '18位身份证号'}),
            'address': forms.TextInput(attrs={'placeholder': '联系地址'}),
        }


class HouseForm(forms.ModelForm):
    """房屋表单"""
    class Meta:
        model = House
        fields = ['building', 'unit', 'room', 'area', 'layout', 'status', 'owner']
        widgets = {
            'building': forms.TextInput(attrs={'placeholder': '如: 1'}),
            'unit': forms.TextInput(attrs={'placeholder': '如: 二'}),
            'room': forms.TextInput(attrs={'placeholder': '如: 101'}),
            'area': forms.NumberInput(attrs={'placeholder': '面积(平方米)', 'step': '0.01'}),
            'layout': forms.TextInput(attrs={'placeholder': '如: 3室2厅'}),
        }


class FeeForm(forms.ModelForm):
    """物业费表单"""
    class Meta:
        model = Fee
        fields = ['house', 'amount', 'month', 'status']
        widgets = {
            'month': forms.TextInput(attrs={'placeholder': '格式: 2026-05'}),
            'amount': forms.NumberInput(attrs={'placeholder': '金额(元)', 'step': '0.01'}),
        }


class RepairForm(forms.ModelForm):
    """报修表单"""
    class Meta:
        model = Repair
        fields = ['house', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': '请详细描述报修内容...'}),
        }


class RepairProcessForm(forms.ModelForm):
    """报修处理表单（员工用）"""
    class Meta:
        model = Repair
        fields = ['status', 'staff', 'result']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 3, 'placeholder': '处理结果说明...'}),
        }


class ComplaintForm(forms.ModelForm):
    """投诉建议表单"""
    class Meta:
        model = Complaint
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': '请输入投诉或建议内容...'}),
        }


class ComplaintReplyForm(forms.ModelForm):
    """投诉回复表单（员工用）"""
    class Meta:
        model = Complaint
        fields = ['reply']
        widgets = {
            'reply': forms.Textarea(attrs={'rows': 3, 'placeholder': '回复内容...'}),
        }


class VisitorForm(forms.ModelForm):
    """访客登记表单"""
    class Meta:
        model = Visitor
        fields = ['name', 'phone', 'reason', 'house', 'visit_time']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '访客姓名'}),
            'phone': forms.TextInput(attrs={'placeholder': '访客电话'}),
            'reason': forms.TextInput(attrs={'placeholder': '来访事由，如: 探亲'}),
            'visit_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class NoticeForm(forms.ModelForm):
    """公告表单"""
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '公告标题'}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': '公告内容...'}),
        }


class ProfileForm(forms.ModelForm):
    """业主个人信息修改表单"""
    class Meta:
        model = Owner
        fields = ['gender', 'id_card', 'address']
