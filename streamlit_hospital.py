import streamlit as st
import mysql.connector
import pandas as pd

con=mysql.connector.connect(host="localhost",user="root",password="annmi2004",database="hospital")
cur=con.cursor()
st.set_page_config(page_title='Hospital Management System')
st.title("Hospital Management System")
menu=st.sidebar.selectbox("Menu",['Add Patient','View Patient','View Doctors',
                                  'Search Doctors By Department','Book Appointment',
                                  'View Appointment','Cancel Appointment','Generate Bill','Edit Patient'])
if menu=="Add Patient":
    st.header("Add Patient")
    patient_name=st.text_input("Patient Name")
    age=st.number_input("Age",min_value=1,step=1)
    phone=st.text_input("Phone Number")
    if st.button("Add Patient"):
        sql="""INSERT INTO patients(patient_name,age,phone) VALUES(%s,%s,%s)"""
        cur.execute(sql,(patient_name,age,phone))
        con.commit()
        st.success("Patient Added Successfully")
elif menu=="View Patient":
    st.header("Patient")
    cur.execute("SELECT * FROM patients")
    data=cur.fetchall()
    df = pd.DataFrame(data,columns=['Patient ID','Name','Age','Phone'])
    st.dataframe(df)
elif menu=="View Doctors":
    st.header("Doctors")
    query="""select d.doctor_id,d.doctor_name,d.specialization,dep.dep_name,d.status,d.fees
    from doctors d join departments dep on dep.dep_id=d.dep_id"""
    cur.execute(query)
    data=cur.fetchall()
    df=pd.DataFrame(data,columns=['doctor_id','doctor_name','specialization',
                                  'dep_name','status','fees'])
    st.dataframe(df)
elif menu=="Search Doctors By Department":
    st.header("Search Doctors")
    cur.execute("select dep_name from departments")
    depts=[x[0] for x in cur.fetchall()]
    dept=st.selectbox("Select Department",depts)
    if st.button("Search"):
        query="""select d.doctor_id,d.doctor_name,d.specialization,d.status 
        from doctors d join departments dep on dep.dep_id=d.dep_id where dep.dep_name=%s"""
        cur.execute(query,(dept,))
        data=cur.fetchall()
        df = pd.DataFrame(data,columns=['doctor_id','doctor_name','specialization','status'])
        st.dataframe(df)
elif menu=="Book Appointment":
    st.header("Book Appointment")
    patient_id=st.number_input("Patient ID",min_value=1)
    doctor_id=st.number_input("Doctor ID",min_value=1)
    appointment_date=st.date_input("Appointment Date")
    if st.button("Book"):
        cur.execute("""select * from appointments where doctor_id=%s and 
                    appointment_date=%s""",(doctor_id,appointment_date))
        if cur.fetchone():
            st.error("Doctor already Booked!")
        else:
            cur.execute("""insert into appointments(patient_id,doctor_id,appointment_date)
                 values (%s,%s,%s)""",(patient_id,doctor_id,appointment_date))
            con.commit()
            st.success("Appointment Book Successfully")
elif menu=='View Appointment':
    st.header("View Appointment")
    query="""select a.appointment_id,p.patient_name,d.doctor_name,dep.dep_name,
    a.appointment_date from appointments a join patients p on p.patient_id=a.patient_id 
    join doctors d on d.doctor_id=a.doctor_id join departments dep on dep.dep_id=d.dep_id"""
    cur.execute(query)
    data=cur.fetchall()
    df=pd.DataFrame(data,columns=['appointment_id','patient_name','doctor_name','dep_name',
                                      'appointment_date'])
    st.dataframe(df)
elif menu=="Cancel Appointment":
    st.header("Cancel Appointment")
    appointment_id=st.number_input("Appointment ID",min_value=1)
    if st.button("Cancel"):
        cur.execute("""delete from appointments where appointment_id=%s""",
                    (appointment_id,))
        con.commit()
        st.success("Appointment Cancel Successfully")
elif menu=="Generate Bill":
    st.header("Generate Bill")
    patient_id=st.number_input("Patient ID",min_value=1)
    if st.button("Generate"):
        query="""select d.doctor_name,dep.dep_name,d.fees from appointments a 
        join doctors d on a.doctor_id=d.doctor_id join departments dep on d.dep_id-dep.dep_id
        where a.patient_id=%s order by a.appointment_id desc limit 1"""
        cur.execute(query,(patient_id,))
        result=cur.fetchone()
        if result:
            doctor_name=result[0]
            dep_name=result[1]
            fee=result[2]
            cur.execute("""insert into bills(patient_id,amount)values (%s,%s)""",
                        (patient_id,fee))
            con.commit()
            st.success(f"Bill Generated Successfully")
            st.write('Patient ID:',patient_id)
            st.write('Doctor:',doctor_name)
            st.write('Department:',dep_name)
            st.write('Consultation Fee:',fee)
        else:
            st.error("No appoitment not found")
