import tkinter
from tkinter import ttk
from tkinter import messagebox
import sqlite3

conn =  sqlite3.connect('tracks.db')

def clear_form():
    tittle_entry.delete(0, 'end')
    category_combobox.set("")
    rating_spinbox.set(0)
    review_textarea.delete("1.0", "end")
    
def data_save():
    title = tittle_entry.get()
    category = category_combobox.get()
    rating = int(rating_spinbox.get())
    review = review_textarea.get("1.0", "end-1c")

    if title and category and review and rating:

        print("Title: ",title, "Category  : ",category)
        print("Rating: ",rating)
        print("Review: \n",review )

        # creating table
        conn = sqlite3.connect('tracks.db')
        table_create_query = '''CREATE TABLE IF NOT EXISTS tracks (
            "id"	INTEGER NOT NULL UNIQUE,
            "title"	TEXT NOT NULL,
            "category"	TEXT NOT NULL,
            "rating"	INTEGER NOT NULL,
            "review"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
                    );'''
        
        try:
            conn.execute(table_create_query)
            insert_data_query = '''INSERT INTO tracks (Title, Category, Rating, Review)
            VALUES (?, ?, ?, ?)'''
            insert_data_tuple=(title,category,rating,review)
            cursor = conn.cursor()
            cursor.execute(insert_data_query, insert_data_tuple)
            conn.commit()
            conn.close() 
            clear_form()
        except sqlite3.Error as e:
            print("An error occurred:", e)

    else:
        tkinter.messagebox.showwarning(tittle="error",message="Feilds are either null or no connection null please completely fill")
def load_data():
    # 1. Clear the treeview first (this works fine)
    for item in tree.get_children():
        tree.delete(item)
    
    # 2. Define conn OUTSIDE the try block or at the very start of it
    conn = None 
    try:
        conn = sqlite3.connect('tracks.db')
        load_query = "SELECT * FROM tracks"
        cursor = conn.execute(load_query)
        for row in cursor:
            tree.insert('', 'end', values=row)
    except sqlite3.OperationalError as e:
        print(f"Table not found or DB error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 3. Only close if conn was actually created
        if conn:
            conn.close()

def delete_review():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a review to delete.")
        return
    
    item_id = tree.item(selected_item)['values'][0]
    if messagebox.askyesno("Confirm", "Are you sure you want to delete this review?"):
        conn = sqlite3.connect('tracks.db')
        delete_query = '''DELETE FROM tracks WHERE id=?'''
        conn.execute(delete_query, (item_id,))
        conn.commit()
        conn.close()
        load_data()

def edit_review():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a review to edit.")
        return
    
    values = tree.item(selected_item)['values']
    
    # Simple Edit Window
    edit_win = tkinter.Toplevel(window)
    edit_win.title("Edit Review")
    
    tkinter.Label(edit_win, text="Title").pack()
    e_title = tkinter.Entry(edit_win)
    e_title.insert(0, values[1])
    e_title.pack()

    tkinter.Label(edit_win, text="Rating").pack()
    e_rating = ttk.Spinbox(edit_win, from_=0, to=5)
    e_rating.set(values[3])
    e_rating.pack()

    tkinter.Label(edit_win, text="Review").pack()
    e_review = tkinter.Entry(edit_win)
    e_review.insert(2, values[4])
    e_review.pack()

    def update_db():
        conn = sqlite3.connect('tracks.db')
        edit_query ='''UPDATE tracks SET Title=?, Rating=? WHERE id=?'''
        conn.execute(edit_query, 
                    (e_title.get(), e_rating.get(), values[0]))
        conn.commit()
        conn.close()
        edit_win.destroy()
        load_data()

    tkinter.Button(edit_win, text="Update", command=update_db).pack(pady=10)

conn.close()

window = tkinter.Tk()
window.title("Entertainment Reviews")


notebook = ttk.Notebook(window)
tab1 = tkinter.Frame(notebook)
tab2 = tkinter.Frame(notebook)
notebook.add(tab1, text="Add New Review")
notebook.add(tab2, text="Manage Reviews")
notebook.pack(expand=True, fill="both")


frame = tkinter.Frame(tab1)
frame.pack()

info_frame = tkinter.LabelFrame(frame, text="Enttertainment information: ")
info_frame.grid(row=0,column=0,padx=25,pady=20)

# form
tittle_label = tkinter.Label(info_frame,text="Tittle: ")
tittle_label.grid(row=0,column=0)

category_label = tkinter.Label(info_frame,text="Category: ")
category_label.grid(row=0,column=2)

rating_label = tkinter.Label(info_frame,text="Rate(out of 5): ")
rating_label.grid(row=1,column=0)

# For consistent padding x and y accross the frame
for widget in info_frame.winfo_children():
    widget.grid_configure(padx=10,pady=5)

# Review text area frame
review_frame = tkinter.LabelFrame(frame, text="Your Review: ")
review_frame.grid(row=1,column=0,padx=25,pady=20,sticky="news")


review_label = tkinter.Label(review_frame,text="Write your heart out...")
review_label.grid(row=0,column=0)

Submit_button = tkinter.Button(review_frame,text="Save Review", command=data_save)
Submit_button.grid(row=2,column=0,sticky="news")



for widget in review_frame.winfo_children():
    widget.grid_configure(padx=15,pady=15)


tittle_entry = tkinter.Entry(info_frame)
tittle_entry.grid(row=0,column=1,padx=25,pady=20)
category_combobox = ttk.Combobox(info_frame,values=["","Movie","Book","Documentry"])
category_combobox.grid(row=0,column=3,padx=25,pady=20)
rating_spinbox = ttk.Spinbox(info_frame,from_=0,to=5)
rating_spinbox.grid(row=1,column=1,padx=25,pady=20)

review_textarea = tkinter.Text(review_frame, width=70, height=10)
review_textarea.grid(row=1,column=0,sticky="news")

# 
# 
# 

# --- TAB 2: VIEW/EDIT/DELETE ---
tree_frame = tkinter.Frame(tab2)
tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

columns = ('id', 'title', 'category', 'rating', 'review')
tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

# Define Headings
tree.heading('id', text='ID')
tree.heading('title', text='Title')
tree.heading('category', text='Category')
tree.heading('rating', text='Rating')
tree.heading('review', text='Review')

tree.column('id', width=30)
tree.column('review', width=200)
tree.pack(fill="both", expand=True)

btn_frame = tkinter.Frame(tab2)
btn_frame.pack(fill="x", padx=10, pady=5)

tkinter.Button(btn_frame, text="Refresh List", command=load_data).pack(side="left", padx=5)
tkinter.Button(btn_frame, text="Edit Selected", command=edit_review).pack(side="left", padx=5)
tkinter.Button(btn_frame, text="Delete Selected", command=delete_review, bg="red", fg="white").pack(side="right", padx=5)

window.mainloop()
