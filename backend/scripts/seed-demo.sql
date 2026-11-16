BEGIN;
-- Ten synthetic leads: 4 hot, 3 warm, 3 cold; no stored priority label.
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Альфа', 'vph06-seed-01@example.com', 'Учебный автопарк', 'До 10 сотрудников', 'Сотрудник', '1 автомобиль', 'Сегодня', 45000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-01@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Бета', 'vph06-seed-02@example.com', 'Учебный автопарк', '11-50 сотрудников', 'Руководитель', '1 автомобиль', 'В течение 7 дней', 45000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-02@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Гамма', 'vph06-seed-03@example.com', 'Учебный автопарк', '51-250 сотрудников', 'Сотрудник', '3 автомобиля', 'Срочно', 15000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-03@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Дельта', 'vph06-seed-04@example.com', 'Учебный автопарк', '11-50 сотрудников', 'Сотрудник', '10 автомобилей', 'В течение 3 дней', 20000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-04@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Эпсилон', 'vph06-seed-05@example.com', 'Учебный автопарк', '', 'Сотрудник', '1 автомобиль', 'В течение недели', 15000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-05@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Дзета', 'vph06-seed-06@example.com', 'Учебный автопарк', '', 'Руководитель', '1 автомобиль', 'В течение месяца', 30000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-06@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Эта', 'vph06-seed-07@example.com', 'Учебный автопарк', '11-50 сотрудников', 'Сотрудник', '1 автомобиль', 'Не срочно', 45000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-07@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Тета', 'vph06-seed-08@example.com', 'Учебный автопарк', 'До 10 сотрудников', 'Сотрудник', '1 автомобиль', 'Без спешки', 15000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-08@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Йота', 'vph06-seed-09@example.com', 'Учебный автопарк', '', 'Клиент', '1 автомобиль', 'Срок не определён', 15000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-09@example.com');
INSERT INTO applications (service_id, name, contact, business, company_size, role, task_scope, deadline, budget, contact_method, contact_time, comment)
SELECT s.id, 'VPh06 / Каппа', 'vph06-seed-10@example.com', 'Учебный автопарк', '', 'Сотрудник', '1 автомобиль', 'В течение месяца', 15000, 'Email', 'В рабочее время', 'VPH06-SEED: вымышленные данные для проверки ранжирования' FROM services s WHERE s.name='Полировка'
AND NOT EXISTS (SELECT 1 FROM applications WHERE contact='vph06-seed-10@example.com');
COMMIT;
