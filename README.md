**วิธี Run**

1. python -m venv venv
2. venv\Scripts\activate
3. pip install -r requirement.txt
4. python seed_data.py
5. python run.py
6. เปิด http://127.0.0.1:5000/ ใน Browser

**MVC Mapping**

1. Model (Data และ Business Rules)

	1.1.) ระบุใน models.py ด้วย SQLAlchemy ORM
   
	1.2.) มีคลาส User, Project, RewardTier, Pledge
   
	1.3.) Encapsulate โครงสร้างตาราง (คอลัมน์, Constraint, ความสัมพันธ์) และ Business logic (เช่น Project.progress_pct(), Project.is_success(), etc.)
   
	1.4.) มีกฎการใช้ข้อมูล (เช่น Foreign key, non-null)

3. View (User Interface)

	2.1.) HTML templates ต่างๆ ใน index.html, detail.html, stats.html, login.html, base.html
   
	2.2.) ใส่สไตล์ด้วย style.css
   
	2.3.) แสดงรายการโครงการ รายละเอียดโครงการ สถิติ ฟอร์มในการ Login และ Pledge

5. Controller (Logic ของแอพ และ Routes)

	3.1.) ใน controllers จะมี auth.py ทำ login/logout และ projects.py ทำรายการโครงการ รายละเอียดโครงการ การ Pledge และสถิติ
   
	3.2.) Controller รับ Request, ใช้ Business rule, Query และ อัพเดต Model และสร้าง View ที่ถูกต้อง


**Routes/Actions ที่สำคัญ**

1. Authentication
   
	1.1.) GET /login: แสดงหน้า Login
   
	1.2.) POST /login: Auth ตัว User (user/pass)
   
	1.3.) GET /logout: ปิด Session และ Log out

3. โครงการ
   
	2.1.) GET /: หน้ารวมโครงการ รองรับการค้นหา กรองตามหมวดหมู่ และการเรียงลำดับ
   
	2.2.) GET /project/<project_id>: รายละเอียดโครงการ เป้าหมาย ความคืบหน้า ระดับรางวัล
   
	2.3.) POST /project/<project_id>/pledge: สร้าง Pledge รองรับ Business rules และถ้า Success จะ Update ยอดเงิน ลดจำนวนโควตา ถ้า Failure จะเพิ่ม rejection_count

5. สถิติ
   
	3.1.) GET /stats: หน้าสถิติ แสดงจำนวนโครงการที่สำเร็จ จำนวนโครงการที่ไม่สำเร็จ และตารางแสดงสถานะของทุกโครงการ
