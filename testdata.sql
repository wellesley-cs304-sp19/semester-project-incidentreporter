use c9;

delete from user;

insert into user (BNUM, name, email, isAdmin, role) values (00000001, "Student 1", "student1@wellesley.edu", false, "student");
insert into user (BNUM, name, email, isAdmin, role) values (00000002, "Student 2", "student2@wellesley.edu", false, "student");
insert into user (BNUM, name, email, isAdmin, role) values (00000003, "Student 3", "student3@wellesley.edu", false, "student");
insert into user (BNUM, name, email, isAdmin, role) values (00000004, "Student 4", "student4@wellesley.edu", false, "student");
insert into user (BNUM, name, email, isAdmin, role) values (00000005, "Student 5", "student5@wellesley.edu", false, "student");
insert into user (BNUM, name, email, isAdmin, role) values (00000000, "Admin", "admin@wellesley.edu", true, "facstaff");
insert into user (BNUM, name, email, isAdmin, role) values (10000000, "FacStaff 1", "facstaff1@wellesley.edu", false, "facstaff");
insert into user (BNUM, name, email, isAdmin, role) values (20000000, "FacStaff 2", "facstaff2@wellesley.edu", false, "facstaff");
insert into user (BNUM, name, email, isAdmin, role) values (30000000, "FacStaff 3", "facstaff 3@wellesley.edu", false, "facstaff");
insert into user (BNUM, name, email, isAdmin, role) values (40000000, "FacStaff 4", "Facstaff 4@wellesley.edu", false, "facstaff");

delete from incident; 
insert into incident (reporterID, reportedID, advocateID, location, category, dateOfIncident, anonymousToAll, anonymousToReported, description) 
    values (00000001, 10000000, 20000000, "sci", "racism", "06-02-2019", false, false, "test");


