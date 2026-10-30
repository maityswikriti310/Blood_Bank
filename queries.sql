
USE blood_bank;

-- 1. Display all donors
SELECT * FROM donor;

-- 2. Display all patients
SELECT * FROM patient;

-- 3. Display all hospitals
SELECT * FROM hospital;

-- 4. Display all blood requests
SELECT * FROM blood_request;

-- 5. Display all blood stock
SELECT * FROM blood_stock;

-- 6. Display all donations
SELECT * FROM donation;

-- 7. Display donors in alphabetical order
SELECT * FROM donor
ORDER BY donor_id ASC;

-- 8. Display patients in alphabetical order
SELECT * FROM patient
ORDER BY patient_name ASC;

-- 9. Display hospitals in alphabetical order
SELECT * FROM hospital
ORDER BY hospital_name ASC;

-- 10. Display the latest blood requests first
SELECT * FROM blood_request
ORDER BY request_id DESC;


-- 11. Count total donors
SELECT COUNT(*) AS total_donors
FROM donor;

-- 12. Count total patients
SELECT COUNT(*) AS total_patients
FROM patient;

-- 13. Count total hospitals
SELECT COUNT(*) AS total_hospitals
FROM hospital;

-- 14. Count total blood requests
SELECT COUNT(*) AS total_requests
FROM blood_request;

-- 15. Count total donations
SELECT COUNT(*) AS total_donations
FROM donation;


-- 16. Show donations with donor details
SELECT donation.*, donor.*
FROM donation
JOIN donor
ON donation.donor_id = donor.donor_id;

-- 17. Show blood requests with patient details
SELECT blood_request.*, patient.*
FROM blood_request
JOIN patient
ON blood_request.patient_name = patient.patient_name;

-- 18. Show donors and their donations
SELECT donor.donor_id, donor.name,
       donation.donation_date, donation.units_donated
FROM donor
JOIN donation
ON donor.donor_id = donation.donor_id;

-- 19. Show all blood requests, including patient details
SELECT blood_request.request_id,
       blood_request.patient_name,
       blood_request.blood_group,
       blood_request.units_needed,
       patient.age, patient.phone
FROM blood_request
JOIN patient
ON blood_request.patient_name = patient.patient_name;

-- 20. Show blood stock details
SELECT *
FROM blood_stock;


-- 21. Find donors whose ID is greater than the average donor ID
SELECT *
FROM donor
WHERE donor_id > (
    SELECT AVG(donor_id)
    FROM donor
);

-- 22. Find requests needing more units than the average
SELECT *
FROM blood_request
WHERE units_needed > (
    SELECT AVG(units_needed)
    FROM blood_request
);

-- 23. Find patients whose blood group appears in a blood request
SELECT *
FROM patient
WHERE blood_group IN (
    SELECT blood_group
    FROM blood_request
);


-- 24. Find donors who have made at least one donation
SELECT *
FROM donor d
WHERE EXISTS (
    SELECT 1
    FROM donation dn
    WHERE dn.donor_id = d.donor_id
);

-- 25. Find patients who have made a blood request
SELECT *
FROM patient p
WHERE EXISTS (
    SELECT 1
    FROM blood_request br
    WHERE br.patient_name = p.patient_name
);
