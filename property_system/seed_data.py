"""
填充演示数据脚本
"""
import os, sys, random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_system.settings')
import django; django.setup()
from property.models import User, Owner, House, Fee, Repair, Complaint, Visitor, Notice

print('正在填充演示数据...')

# ============ 1. 创建员工 ============
staff_data = [
    ('staff02', 'staff123', '赵建国', '13900001111'),
    ('staff03', 'staff123', '钱小丽', '13900002222'),
    ('staff04', 'staff123', '孙志强', '13900003333'),
    ('staff05', 'staff123', '周美玲', '13900004444'),
]
for username, pwd, name, phone in staff_data:
    u, created = User.objects.get_or_create(username=username, defaults={
        'role': 'staff', 'name': name, 'phone': phone
    })
    if created:
        u.set_password(pwd)
        u.save()
        print(f'  员工: {name} (NEW)')

# ============ 2. 创建业主 + 用户 ============
owner_data = [
    ('owner02', 'owner123', '王建国', '13811110001', '男', '440101198502150011', '幸福小区1栋201'),
    ('owner03', 'owner123', '刘美丽', '13811110002', '女', '440101199003200022', '幸福小区2栋304'),
    ('owner04', 'owner123', '陈大明', '13811110003', '男', '440101197508100033', '幸福小区3栋102'),
    ('owner05', 'owner123', '林小红', '13811110004', '女', '440101198812050044', '幸福小区1栋503'),
    ('owner06', 'owner123', '黄志伟', '13811110005', '男', '440101199206180055', '幸福小区4栋201'),
    ('owner07', 'owner123', '吴小芳', '13811110006', '女', '440101198303220066', '幸福小区2栋601'),
    ('owner08', 'owner123', '郑国栋', '13811110007', '男', '440101199510110077', '幸福小区5栋402'),
    ('owner09', 'owner123', '冯美云', '13811110008', '女', '440101198907300088', '幸福小区3栋205'),
    ('owner10', 'owner123', '何志明', '13811110009', '男', '440101199308250099', '幸福小区6栋301'),
    ('owner11', 'owner123', '罗秀英', '13811110010', '女', '440101198105140111', '幸福小区7栋502'),
]

owners = []
for username, pwd, name, phone, gender, id_card, addr in owner_data:
    u, created = User.objects.get_or_create(username=username, defaults={
        'role': 'owner', 'name': name, 'phone': phone
    })
    if created:
        u.set_password(pwd)
        u.save()
    o, _ = Owner.objects.get_or_create(user=u, defaults={
        'gender': gender, 'id_card': id_card, 'address': addr
    })
    owners.append(o)
    print(f'  业主: {name} ({"NEW" if created else "OK"})')

all_owners = list(Owner.objects.all())

# ============ 3. 创建房屋 ============
house_layouts = [
    # owner, building, unit, room, area, layout, status
    (all_owners[1], '1', '二', '302', 89.50, '2室2厅', 'occupied'),
    (all_owners[2], '2', '一', '304', 120.00, '3室2厅', 'occupied'),
    (all_owners[3], '3', '一', '102', 95.80, '2室2厅', 'occupied'),
    (all_owners[4], '1', '二', '503', 75.00, '2室1厅', 'occupied'),
    (all_owners[5], '4', '一', '201', 105.00, '3室2厅', 'occupied'),
    (all_owners[6], '2', '二', '601', 130.00, '4室2厅', 'occupied'),
    (all_owners[7], '5', '一', '402', 88.00, '2室2厅', 'occupied'),
    (all_owners[8], '3', '一', '205', 92.50, '3室1厅', 'occupied'),
    (all_owners[9], '6', '一', '301', 110.00, '3室2厅', 'occupied'),
    (all_owners[10], '7', '二', '502', 98.00, '2室2厅', 'occupied'),
]
# 给第一个业主也创建房屋
if not House.objects.filter(owner=all_owners[0]).exists():
    house_layouts.insert(0, (all_owners[0], '1', '一', '101', 100.00, '3室2厅', 'occupied'))

# 空置房
vacant_houses = [
    ('2', '一', '201', 86.00, '2室2厅'),
    ('3', '二', '301', 92.50, '3室1厅'),
    ('4', '二', '502', 78.00, '2室1厅'),
    ('5', '二', '101', 115.00, '3室2厅'),
    ('6', '一', '102', 88.00, '2室2厅'),
]

all_houses = []
for item in house_layouts:
    h, created = House.objects.get_or_create(
        building=item[1], unit=item[2], room=item[3],
        defaults={'owner': item[0], 'area': item[4], 'layout': item[5], 'status': item[6]}
    )
    all_houses.append(h)
    if created:
        print(f'  房屋: {h.full_address} ({item[4]}m², {item[5]})')

for building, unit, room, area, layout in vacant_houses:
    h, created = House.objects.get_or_create(
        building=building, unit=unit, room=room,
        defaults={'area': area, 'layout': layout, 'status': 'vacant'}
    )
    all_houses.append(h)
    if created:
        print(f'  空置房: {h.full_address} ({area}m², {layout})')

# ============ 4. 创建物业费记录 ============
months = ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05']
for house in all_houses[:11]:  # 只给已入住的房屋生成
    for month in months:
        amount = round(float(house.area) * 2.5, 2)  # 2.5元/m²
        fee, created = Fee.objects.get_or_create(
            house=house, month=month,
            defaults={'amount': amount, 'status': 0}
        )
        if not created:
            continue
        # 1-4月随机已缴
        if month != '2026-05' and random.random() > 0.3:
            fee.status = 1
            fee.pay_time = datetime(2026, int(month[5:]), random.randint(1, 25), 10, 30)
            fee.save()
print('  物业费账单已生成（2026-01 至 2026-05）')

# ============ 5. 创建报修记录 ============
repair_contents = [
    '卫生间水管漏水，需要紧急维修',
    '客厅空调不制冷，夏天快到了',
    '厨房下水道堵塞，排水很慢',
    '入户门锁损坏，无法正常开关',
    '阳台地漏反味严重',
    '卧室墙面有裂缝，担心安全隐患',
    '电路跳闸频繁，需要检查线路',
    '热水器水温不稳定',
    '窗户密封条老化，漏风严重',
    '楼顶有渗水痕迹，需要防水处理',
    '电梯间灯不亮，影响出行',
    '门禁对讲机故障，无法通话',
]
staff_list = list(User.objects.filter(role='staff'))
all_houses_with_owner = list(House.objects.exclude(owner__isnull=True))

for i, row in enumerate(repair_contents):
    owner = all_owners[i % len(all_owners)]
    house = House.objects.filter(owner=owner).first()
    if not house:
        continue
    days_ago = random.randint(1, 60)
    status = random.choices([0, 1, 2], weights=[3, 3, 4])[0]
    r = Repair.objects.create(
        owner=owner, house=house, content=row,
        submit_time=datetime.now() - timedelta(days=days_ago),
        status=status
    )
    if status in [1, 2]:
        r.staff = random.choice(staff_list)
        if status == 2:
            r.process_time = r.submit_time + timedelta(days=random.randint(1, 5))
            r.result = random.choice(['已维修完成', '已更换配件', '已疏通', '已修复'])
        r.save()
print(f'  {len(repair_contents)} 条报修记录已创建')

# ============ 6. 创建投诉建议 ============
complaint_contents = [
    '小区门口垃圾堆放时间过长，异味严重',
    '建议在小区内增加儿童游乐设施',
    '地下车库照明不足，晚上很暗',
    '物业公司服务态度需要改善',
    '小区绿化带需要修剪，杂草太多',
    '建议设置快递柜，方便业主取件',
    '电梯内经常有人吸烟，请加强管理',
    '周末施工噪音太大，影响休息',
]
for i, content in enumerate(complaint_contents):
    owner = all_owners[i % len(all_owners)]
    days_ago = random.randint(5, 90)
    c = Complaint.objects.create(
        owner=owner, content=content,
        submit_time=datetime.now() - timedelta(days=days_ago),
        status=random.choice([0, 0, 1])
    )
    if c.status == 1:
        c.reply = random.choice([
            '已安排人员处理，感谢您的反馈',
            '我们会尽快改善，谢谢建议',
            '已将您的意见转达相关部门',
        ])
        c.reply_time = c.submit_time + timedelta(days=random.randint(1, 3))
        c.save()
print(f'  {len(complaint_contents)} 条投诉建议已创建')

# ============ 7. 创建访客记录 ============
visitor_data = [
    ('孙阿姨', '15600001111', '探亲', 0),
    ('王师傅', '15600002222', '送货', 2),
    ('刘先生', '15600003333', '拜访朋友', 5),
    ('陈女士', '15600004444', '看房', 7),
    ('张快递', '15600005555', '快递派送', 1),
    ('赵维修', '15600006666', '上门维修', 3),
    ('杨小姐', '15600007777', '探访', 4),
    ('吴先生', '15600008888', '参加聚会', 6),
    ('快递员小周', '15600009999', '快递', 0),
    ('外卖小哥', '15600000000', '送餐', 9),
]
for name, phone, reason, idx in visitor_data:
    house = all_houses[idx % len(all_houses)]
    days_ago = random.randint(0, 30)
    Visitor.objects.create(
        name=name, phone=phone, reason=reason, house=house,
        visit_time=datetime.now() - timedelta(days=days_ago),
        staff=random.choice(staff_list)
    )
print(f'  {len(visitor_data)} 条访客记录已创建')

# ============ 8. 创建公告 ============
publisher = User.objects.filter(role='staff').first()
notice_data = [
    ('关于小区停水通知', '各位业主：因管道维修，本小区将于6月5日上午8:00至下午18:00停水，请提前做好储水准备。如有疑问请联系物业办公室。'),
    ('端午节假期安全提示', '端午节假期将至，请各位业主注意用电安全，外出时关好门窗，车辆停放地下室请锁好车门。祝大家节日快乐！'),
    ('小区电梯年检通知', '定于6月10日至6月12日对小区所有电梯进行年度安全检查，届时各楼栋电梯将轮流停运，请业主提前做好准备。'),
    ('物业费缴纳提醒', '2026年第二季度物业费已开始收缴，请未缴费的业主尽快前往物业办公室或通过线上方式缴纳。逾期将产生滞纳金。'),
    ('关于开展消防演练的通知', '为提高小区消防安全意识，定于6月20日下午3点在小广场举行消防演练，欢迎各位业主积极参与。'),
    ('小区门禁系统升级公告', '小区门禁系统将于近期升级为人脸识别系统，请各位业主携带身份证件到物业办公室录入人脸信息。'),
]
for title, content in notice_data:
    days_ago = random.randint(0, 45)
    Notice.objects.create(
        title=title, content=content, publisher=publisher,
        publish_time=datetime.now() - timedelta(days=days_ago),
        is_public=random.choice([True, True, True, False])
    )
print(f'  {len(notice_data)} 条公告已创建')

# ============ 统计 ============
print(f'\n{"="*50}')
print(f'  演示数据填充完成!')
print(f'  用户: {User.objects.count()} 人 (管理员1 + 员工{User.objects.filter(role="staff").count()} + 业主{User.objects.filter(role="owner").count()})')
print(f'  房屋: {House.objects.count()} 间')
print(f'  物业费: {Fee.objects.count()} 条')
print(f'  报修: {Repair.objects.count()} 条')
print(f'  投诉: {Complaint.objects.count()} 条')
print(f'  访客: {Visitor.objects.count()} 条')
print(f'  公告: {Notice.objects.count()} 条')
print(f'{"="*50}')
