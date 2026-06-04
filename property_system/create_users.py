"""创建初始用户"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_system.settings')
import django; django.setup()
from property.models import User, Owner

def make_user(username, password, role, name, phone):
    u, created = User.objects.get_or_create(
        username=username,
        defaults={'role': role, 'name': name, 'phone': phone}
    )
    u.set_password(password)
    u.role = role
    u.name = name
    u.phone = phone
    u.save()
    tag = "NEW" if created else "OK"
    print(f'  {username} ({role}) = {name} [{tag}]')
    return u

print('Creating initial users...')
make_user('admin', 'admin123', 'admin', '系统管理员', '13800000001')
u = make_user('staff01', 'staff123', 'staff', '张员工', '13800000002')
u = make_user('owner01', 'owner123', 'owner', '李业主', '13800000003')
Owner.objects.get_or_create(user=u, defaults={'gender': '男', 'id_card': '440101199001011234'})
print('Done.')
