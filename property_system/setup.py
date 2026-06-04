"""
一键部署脚本 - 小区物业管理系统
功能: 启动数据库 → 建库 → 迁移 → 执行SQL → 创建用户 → 启动服务
"""
import os
import sys
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_system.settings')

# 读取数据库配置
from django.conf import settings
DB = settings.DATABASES['default']

print('=' * 60)
print('  小区物业管理系统 - 一键部署')
print('=' * 60)


# ============ 步骤0: 启动数据库 ============
def find_mariadb_bin():
    """查找 MariaDB/MySQL bin 目录"""
    paths = [
        r'C:\Program Files\MariaDB 12.2\bin',
        r'C:\Program Files\MariaDB\bin',
        r'C:\Program Files (x86)\MariaDB 12.2\bin',
        r'C:\Program Files\MySQL\MySQL Server 8.0\bin',
        r'C:\Program Files\MySQL\MySQL Server 8.4\bin',
    ]
    for p in paths:
        exe = os.path.join(p, 'mariadb.exe')
        if not os.path.exists(exe):
            exe = os.path.join(p, 'mysql.exe')
        if os.path.exists(exe):
            return p
    return None


def start_database():
    """尝试连接数据库，失败则尝试启动"""
    import pymysql
    try:
        conn = pymysql.connect(
            host=DB['HOST'], port=int(DB['PORT']),
            user=DB['USER'], password=DB['PASSWORD'],
            charset='utf8mb4', connect_timeout=3
        )
        conn.close()
        print('  数据库已运行')
        return True
    except Exception:
        pass

    bin_dir = find_mariadb_bin()
    if not bin_dir:
        print('  未找到 MariaDB/MySQL 安装，请手动安装')
        return False

    # 尝试启动 Windows 服务
    service_names = ['MariaDB', 'MySQL', 'MySQL80', 'MySQL84']
    for svc in service_names:
        try:
            subprocess.run(['sc', 'start', svc], capture_output=True, timeout=5)
            time.sleep(2)
            return True
        except Exception:
            continue

    # 直接启动 mariadbd
    print('  正在启动 MariaDB...')
    mariadbd = os.path.join(bin_dir, 'mariadbd.exe')
    if not os.path.exists(mariadbd):
        mariadbd = os.path.join(bin_dir, 'mysqld.exe')
    if os.path.exists(mariadbd):
        subprocess.Popen(
            [mariadbd, '--standalone', '--port=3306'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # 等待启动
        for _ in range(10):
            time.sleep(1)
            try:
                conn = pymysql.connect(
                    host=DB['HOST'], port=int(DB['PORT']),
                    user=DB['USER'], password=DB['PASSWORD'],
                    charset='utf8mb4', connect_timeout=2
                )
                conn.close()
                print('  数据库启动成功')
                return True
            except Exception:
                pass
    print('  无法启动数据库')
    return False


print('\n[0/6] 检查数据库...')
if not start_database():
    print('  数据库不可用，请确认 MariaDB/MySQL 已安装')
    input('\n按任意键退出...')
    sys.exit(1)


# ============ 步骤1: 检查依赖 ============
print('\n[1/6] 检查依赖...')
try:
    import django as _django
    import pymysql as _pymysql
    print(f'  Django {_django.__version__} / pymysql {_pymysql.__version__}')
except ImportError:
    print('  安装依赖...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'django', 'pymysql', '-q'])
    print('  依赖安装完成')


# ============ 步骤2: 创建数据库 ============
print('\n[2/6] 创建数据库...')
import pymysql
conn = pymysql.connect(
    host=DB['HOST'], port=int(DB['PORT']),
    user=DB['USER'], password=DB['PASSWORD'], charset='utf8mb4'
)
cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB['NAME']}` DEFAULT CHARSET utf8mb4")
cursor.close(); conn.close()
print(f'  数据库 [{DB["NAME"]}] 已就绪')


# ============ 步骤3+4: 数据库迁移 ============
print('\n[3/6] 执行 makemigrations...')
os.chdir(BASE_DIR)
subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'property'],
               capture_output=True)
print('  完成')

print('\n[4/6] 执行 migrate...')
ret = subprocess.run([sys.executable, 'manage.py', 'migrate'], capture_output=True, text=True)
if ret.returncode != 0:
    print(f'  错误:\n{ret.stderr}')
    sys.exit(1)
print('  数据表已创建')


# ============ 步骤5: 执行 init_db.sql ============
print('\n[5/6] 执行 SQL 高级功能 (视图/触发器/存储过程)...')
sql_file = os.path.join(BASE_DIR, 'init_db.sql')
bin_dir = find_mariadb_bin()
if bin_dir:
    mariadb_exe = os.path.join(bin_dir, 'mariadb.exe')
    if not os.path.exists(mariadb_exe):
        mariadb_exe = os.path.join(bin_dir, 'mysql.exe')
    # 通过 CLI 管道执行 SQL 文件（支持 DELIMITER 语法）
    with open(sql_file, 'r', encoding='utf-8') as f:
        subprocess.run(
            [mariadb_exe, f'-u{DB["USER"]}', f'-p{DB["PASSWORD"]}', DB['NAME']],
            stdin=f, capture_output=True
        )
    print('  视图/触发器/存储过程 已创建')
else:
    print('  跳过（未找到数据库客户端）')


# ============ 步骤6: 创建初始用户 + 演示数据 ============
print('\n[6/6] 创建用户和演示数据...')
import django; django.setup()

# 运行数据填充脚本
seed_file = os.path.join(BASE_DIR, 'seed_data.py')
if os.path.exists(seed_file):
    subprocess.run([sys.executable, seed_file])
else:
    print('  未找到 seed_data.py，创建基础用户...')
    from property.models import User, Owner
    def create_user(username, password, role, name, phone):
        u, _ = User.objects.get_or_create(
            username=username,
            defaults={'role': role, 'name': name, 'phone': phone}
        )
        u.set_password(password)
        u.role = role; u.name = name; u.phone = phone
        u.save()
        return u
    create_user('admin', 'admin123', 'admin', '系统管理员', '13800000001')
    create_user('staff01', 'staff123', 'staff', '张员工', '13800000002')
    u = create_user('owner01', 'owner123', 'owner', '李业主', '13800000003')
    Owner.objects.get_or_create(user=u, defaults={'gender': '男', 'id_card': '440101199001011234'})

print('\n' + '=' * 60)
print('  部署完成! 正在启动服务器...')
print('')
print('  访问地址: http://127.0.0.1:8000/')
print('')
print('  管理员:   admin   / admin123')
print('  员工:     staff01 / staff123  (共5名员工)')
print('  业主:     owner01 / owner123  (共11名业主)')
print('')
print('  所有账号密码规律: 用户名后加 123')
print('  例如: owner05 / owner123')
print('=' * 60)

# 启动开发服务器
os.chdir(BASE_DIR)
subprocess.run([sys.executable, 'manage.py', 'runserver'])
