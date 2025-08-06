import datetime
import sqlite3
from xmlrpc.client import boolean

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db,detect_types=sqlite3.PARSE_DECLTYPES |sqlite3.PARSE_COLNAMES)
        self.cur = self.conn.cursor()
        #self.cur.execute("CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, part text,customer text, retailer text, price text)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tbl_user (user_id INTEGER,user_name VARCHAR(45) NULL,user_username VARCHAR(45) NULL,user_password VARCHAR(45) NULL,user_date timestamp,PRIMARY KEY (user_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tbl_proj (proj_id INTEGER,proj_name VARCHAR(45) NULL,proj_desc VARCHAR(250) NULL,tasks_bundle INTEGER,user VARCHAR(45) NULL,proj_date timestamp,PRIMARY KEY (proj_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tbl_tasks_bundle_def (bundle_id INTEGER,task_def_id INTEGER,task_inx INTEGER,PRIMARY KEY (bundle_id,task_def_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tbl_task_def (task_def_id INTEGER,task_def_name VARCHAR(45) NULL,task_def_desc VARCHAR(250) NULL,duration INTEGER,PRIMARY KEY (task_def_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tbl_task (task_def_id INTEGER,proj_id INTEGER,task_id INTEGER,task_name VARCHAR(45) NULL,task_desc VARCHAR(250) NULL,task_done VARCHAR(2),task_date timestamp,PRIMARY KEY (task_id))")
        self.newint(False) #'True' if need to create task
        self.conn.commit()

    def fetchAllUsers(self):
        self.cur.execute("SELECT * FROM tbl_user")
        rows = self.cur.fetchall()
        return rows

    def fetchUser(self,user):
        self.cur.execute("SELECT * FROM tbl_user where user_username=?",(user,))
        rows = self.cur.fetchall()
        return rows   

    def fetchProjects(self,user):
        print("Trigger fetchProjects Project")
        self.cur.execute("SELECT * FROM tbl_proj where user=?",(user,))
        rows = self.cur.fetchall()
        print("Number of projects the fetched:",rows.count)
        return rows  

    def newint(self,startdef):
        if (startdef):
            self.cur.execute ("INSERT INTO tbl_task_def VALUES (?,?,?,?)", (1,'פגישה עם נציג','task desc',5))
            self.cur.execute ("INSERT INTO tbl_task_def VALUES (?,?,?,?)", (2,'לשלוח דווח','task desc',5))
            self.cur.execute ("INSERT INTO tbl_task_def VALUES (?,?,?,?)", (3,'עבודה עם שטח','task desc',5))
            self.cur.execute ("INSERT INTO tbl_task_def VALUES (?,?,?,?)", (4,'לשלוח מיי לבנק','task desc',5))
            self.cur.execute ("INSERT INTO tbl_task_def VALUES (?,?,?,?)", (5,'כללי','task desc',5))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (11,1,1))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (11,2,2))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (11,5,3))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (12,3,1))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (12,4,2))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (12,5,3))
            self.cur.execute ("INSERT INTO tbl_tasks_bundle_def VALUES (?,?,?)", (10,5,3))

    def fetchProjectTasks(self,user,ProjectID):
        print("Trigger fetchProjectTasks:",user,ProjectID)
        #self.cur.execute("SELECT * from tbl_tasks_bundle_def where bundle_id = (SELECT tasks_bundle FROM tbl_proj where user=? and proj_id=?)",(user,ProjectID))
        self.cur.execute("SELECT * FROM tbl_task_def WHERE task_def_id in (SELECT task_def_id from tbl_tasks_bundle_def where bundle_id = (SELECT tasks_bundle FROM tbl_proj where user=? and proj_id=?))",(user,ProjectID))
        rows = self.cur.fetchall()
        print('FetchPrint',rows)
        print("Number of Tasks the fetched:",rows.count)
        return rows  

    def fetchTasksforTaskDef(self,taskdefid,ProjectID):
        print("Trigger fetchTasksforTaskDef:",taskdefid,ProjectID) 
        self.cur.execute("SELECT * FROM tbl_task where task_def_id=? and proj_id=?",(taskdefid,ProjectID))
        rows = self.cur.fetchall()
        print('FetchPrint -fetchTasksforTaskDef',rows)
        print("Number of Tasks the fetched-fetchTasksforTaskDef:",rows.count)
        return rows 

    def fetchUserSpecificProject(self,user,project):
        self.cur.execute("SELECT * FROM tbl_proj where user=? and proj_name=?",(user,project,))
        rows = self.cur.fetchall()
        return rows  
    
    def fetchProjSpecificTask(self,taskDefId,projId):
        self.cur.execute("SELECT * FROM tbl_task where task_def_id=? and proj_id=?",(taskDefId,projId,))
        rows = self.cur.fetchall()
        return rows  
    
    def insert(self, user_name,user_username,user_password):
        print("Trigger insert User")
        now = datetime.datetime.now()
        self.cur.execute ("INSERT INTO tbl_user VALUES (NULL, ?,?,?,?)", (user_name, user_username,user_password,now))
        self.conn.commit()
    
    def insertProject(self, proj_name,proj_desc,tasks_bundle,user):
        print("Trigger insert Project")
        now = datetime.datetime.now()
        self.cur.execute ("INSERT INTO tbl_proj VALUES (NULL, ?,?,?,?,?)", (proj_name,proj_desc,tasks_bundle,user,now))
        self.conn.commit()

    def insertTask(self,task_def_id,proj_id,tasks_name,tasks_desc,task_done):
        print("Trigger insert Task")
        now = datetime.datetime.now()
        self.cur.execute ("INSERT INTO tbl_task VALUES (?,?,NULL,?,?,?,?)", (task_def_id,proj_id,tasks_name,tasks_desc,task_done,now))
        self.conn.commit()

    def updateTask(self,proj_id,task_id,tasks_name,tasks_desc,task_done):
        print("Trigger Update  Task")
        self.cur.execute ("UPDATE tbl_task SET task_name=?,task_desc =?,task_done=? where task_id =? and proj_id=?",(tasks_name,tasks_desc,task_done,task_id,proj_id))
        self.conn.commit()

    def remove(self,id):
        self.cur.execute ("DELETE FROM tbl_user WHERE user_id=?",(id))
        self.conn.commit()

    def update(self,id,part,customer, retailer,price):
        self.cur.execute("UPDATE parts SET part =?,customer =?,retailer =?, price = ? WHERE id  = ?", (part, customer,retailer,price,id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


db = Database('BucketList.db') #This commend create the DB
#db.insertProject("Project Name","Project Dec","orenahar@gmail.com")
#db.insertProject("Project Name","Project Dec","or@gmail.com")
#db.insert("11","21","31","41")
#db.insert("12","22","32","42")
#db.insert("13","23","33","43")
#db.insert("14","24","34","44")
