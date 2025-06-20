package com.example.smartreminder;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class DatabaseHelper extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "smartreminder.db";
    private static final int DATABASE_VERSION = 2;
    
    // Reminders table
    private static final String TABLE_REMINDERS = "reminders";
    private static final String KEY_ID = "id";
    private static final String KEY_TITLE = "title";
    private static final String KEY_DESCRIPTION = "description";
    private static final String KEY_DATE = "date";
    private static final String KEY_SHARED_WITH = "shared_with";
    private static final String KEY_OWNER_EMAIL = "owner_email";
    private static final String KEY_IS_SHARED = "is_shared";
    
    // Notes table
    private static final String TABLE_NOTES = "notes";
    private static final String KEY_NOTE_ID = "id";
    private static final String KEY_NOTE_TITLE = "title";
    private static final String KEY_NOTE_CONTENT = "content";
    private static final String KEY_NOTE_CREATED_AT = "created_at";
    private static final String KEY_NOTE_CREATED_BY = "created_by";
    private static final String KEY_NOTE_SHARED_WITH = "shared_with";
    
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
    
    public DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }
    
    @Override
    public void onCreate(SQLiteDatabase db) {
        // Create reminders table
        String CREATE_REMINDERS_TABLE = "CREATE TABLE " + TABLE_REMINDERS + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_TITLE + " TEXT,"
                + KEY_DESCRIPTION + " TEXT,"
                + KEY_DATE + " TEXT,"
                + KEY_SHARED_WITH + " TEXT,"
                + KEY_OWNER_EMAIL + " TEXT,"
                + KEY_IS_SHARED + " INTEGER DEFAULT 0"
                + ")";
        
        // Create notes table
        String CREATE_NOTES_TABLE = "CREATE TABLE " + TABLE_NOTES + "("
                + KEY_NOTE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_NOTE_TITLE + " TEXT,"
                + KEY_NOTE_CONTENT + " TEXT,"
                + KEY_NOTE_CREATED_AT + " TEXT,"
                + KEY_NOTE_CREATED_BY + " TEXT,"
                + KEY_NOTE_SHARED_WITH + " TEXT"
                + ")";
        
        db.execSQL(CREATE_REMINDERS_TABLE);
        db.execSQL(CREATE_NOTES_TABLE);
    }
    
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        if (oldVersion < 2) {
            // Add new columns for sharing
            db.execSQL("ALTER TABLE " + TABLE_REMINDERS + " ADD COLUMN " + KEY_SHARED_WITH + " TEXT");
            db.execSQL("ALTER TABLE " + TABLE_REMINDERS + " ADD COLUMN " + KEY_OWNER_EMAIL + " TEXT");
            db.execSQL("ALTER TABLE " + TABLE_REMINDERS + " ADD COLUMN " + KEY_IS_SHARED + " INTEGER DEFAULT 0");
            
            // Create notes table
            String CREATE_NOTES_TABLE = "CREATE TABLE " + TABLE_NOTES + "("
                    + KEY_NOTE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                    + KEY_NOTE_TITLE + " TEXT,"
                    + KEY_NOTE_CONTENT + " TEXT,"
                    + KEY_NOTE_CREATED_AT + " TEXT,"
                    + KEY_NOTE_CREATED_BY + " TEXT,"
                    + KEY_NOTE_SHARED_WITH + " TEXT"
                    + ")";
            
            db.execSQL(CREATE_NOTES_TABLE);
        }
    }
    
    // Insert a reminder
    public long insertReminder(Reminder reminder) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(KEY_TITLE, reminder.getTitle());
        values.put(KEY_DESCRIPTION, reminder.getDescription());
        values.put(KEY_DATE, reminder.getDate());
        
        // Handle sharing info
        if (reminder.getSharedWith() != null && !reminder.getSharedWith().isEmpty()) {
            values.put(KEY_SHARED_WITH, joinStrings(reminder.getSharedWith()));
        }
        values.put(KEY_OWNER_EMAIL, reminder.getOwnerEmail());
        values.put(KEY_IS_SHARED, reminder.isShared() ? 1 : 0);
        
        long id = db.insert(TABLE_REMINDERS, null, values);
        db.close();
        return id;
    }
    
    // Get all reminders
    public List<Reminder> getAllReminders() {
        List<Reminder> reminderList = new ArrayList<>();
        String selectQuery = "SELECT * FROM " + TABLE_REMINDERS + " ORDER BY " + KEY_DATE + " ASC";
        
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(selectQuery, null);
        
        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(KEY_ID);
                int titleIndex = cursor.getColumnIndex(KEY_TITLE);
                int descIndex = cursor.getColumnIndex(KEY_DESCRIPTION);
                int dateIndex = cursor.getColumnIndex(KEY_DATE);
                int sharedWithIndex = cursor.getColumnIndex(KEY_SHARED_WITH);
                int ownerEmailIndex = cursor.getColumnIndex(KEY_OWNER_EMAIL);
                int isSharedIndex = cursor.getColumnIndex(KEY_IS_SHARED);
                
                if (idIndex != -1 && titleIndex != -1 && descIndex != -1 && dateIndex != -1) {
                    Reminder reminder = new Reminder(
                            cursor.getLong(idIndex),
                            cursor.getString(titleIndex),
                            cursor.getString(descIndex),
                            cursor.getString(dateIndex)
                    );
                    
                    // Set sharing info if available
                    if (sharedWithIndex != -1 && !cursor.isNull(sharedWithIndex)) {
                        String sharedWithStr = cursor.getString(sharedWithIndex);
                        if (sharedWithStr != null && !sharedWithStr.isEmpty()) {
                            reminder.setSharedWith(splitString(sharedWithStr));
                        }
                    }
                    
                    if (ownerEmailIndex != -1 && !cursor.isNull(ownerEmailIndex)) {
                        reminder.setOwnerEmail(cursor.getString(ownerEmailIndex));
                    }
                    
                    if (isSharedIndex != -1) {
                        reminder.setShared(cursor.getInt(isSharedIndex) == 1);
                    }
                    
                    reminderList.add(reminder);
                }
            } while (cursor.moveToNext());
        }
        
        cursor.close();
        db.close();
        return reminderList;
    }
    
    // Get reminders shared with a specific email
    public List<Reminder> getRemindersSharedWith(String email) {
        List<Reminder> sharedReminderList = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        
        // Using SQL LIKE with pattern to find email in the shared_with column
        String selectQuery = "SELECT * FROM " + TABLE_REMINDERS + 
                " WHERE " + KEY_SHARED_WITH + " LIKE ? ORDER BY " + KEY_DATE + " ASC";
        
        Cursor cursor = db.rawQuery(selectQuery, new String[]{"%" + email + "%"});
        
        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(KEY_ID);
                int titleIndex = cursor.getColumnIndex(KEY_TITLE);
                int descIndex = cursor.getColumnIndex(KEY_DESCRIPTION);
                int dateIndex = cursor.getColumnIndex(KEY_DATE);
                int ownerEmailIndex = cursor.getColumnIndex(KEY_OWNER_EMAIL);
                
                if (idIndex != -1 && titleIndex != -1 && descIndex != -1 && dateIndex != -1 && ownerEmailIndex != -1) {
                    Reminder reminder = new Reminder(
                            cursor.getLong(idIndex),
                            cursor.getString(titleIndex),
                            cursor.getString(descIndex),
                            cursor.getString(dateIndex),
                            cursor.getString(ownerEmailIndex),
                            true
                    );
                    sharedReminderList.add(reminder);
                }
            } while (cursor.moveToNext());
        }
        
        cursor.close();
        db.close();
        return sharedReminderList;
    }
    
    // Delete a reminder
    public void deleteReminder(long id) {
        SQLiteDatabase db = this.getWritableDatabase();
        db.delete(TABLE_REMINDERS, KEY_ID + " = ?", new String[]{String.valueOf(id)});
        db.close();
    }
    
    // Update a reminder
    public int updateReminder(Reminder reminder) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(KEY_TITLE, reminder.getTitle());
        values.put(KEY_DESCRIPTION, reminder.getDescription());
        values.put(KEY_DATE, reminder.getDate());
        
        // Handle sharing info
        if (reminder.getSharedWith() != null && !reminder.getSharedWith().isEmpty()) {
            values.put(KEY_SHARED_WITH, joinStrings(reminder.getSharedWith()));
        }
        values.put(KEY_OWNER_EMAIL, reminder.getOwnerEmail());
        values.put(KEY_IS_SHARED, reminder.isShared() ? 1 : 0);
        
        int result = db.update(TABLE_REMINDERS, values, KEY_ID + " = ?", 
                new String[]{String.valueOf(reminder.getId())});
        db.close();
        return result;
    }
    
    // Share a reminder with others
    public int shareReminder(long reminderId, List<String> emails) {
        SQLiteDatabase db = this.getWritableDatabase();
        Reminder reminder = getReminderById(reminderId);
        
        if (reminder != null) {
            for (String email : emails) {
                reminder.addSharedEmail(email);
            }
            reminder.setShared(true);
            return updateReminder(reminder);
        }
        
        return 0;
    }
    
    // Get a reminder by ID
    public Reminder getReminderById(long id) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_REMINDERS, null, KEY_ID + " = ?",
                new String[]{String.valueOf(id)}, null, null, null);
        
        Reminder reminder = null;
        if (cursor != null && cursor.moveToFirst()) {
            int idIndex = cursor.getColumnIndex(KEY_ID);
            int titleIndex = cursor.getColumnIndex(KEY_TITLE);
            int descIndex = cursor.getColumnIndex(KEY_DESCRIPTION);
            int dateIndex = cursor.getColumnIndex(KEY_DATE);
            int sharedWithIndex = cursor.getColumnIndex(KEY_SHARED_WITH);
            int ownerEmailIndex = cursor.getColumnIndex(KEY_OWNER_EMAIL);
            int isSharedIndex = cursor.getColumnIndex(KEY_IS_SHARED);
            
            if (idIndex != -1 && titleIndex != -1 && descIndex != -1 && dateIndex != -1) {
                reminder = new Reminder(
                        cursor.getLong(idIndex),
                        cursor.getString(titleIndex),
                        cursor.getString(descIndex),
                        cursor.getString(dateIndex)
                );
                
                // Set sharing info if available
                if (sharedWithIndex != -1 && !cursor.isNull(sharedWithIndex)) {
                    String sharedWithStr = cursor.getString(sharedWithIndex);
                    if (sharedWithStr != null && !sharedWithStr.isEmpty()) {
                        reminder.setSharedWith(splitString(sharedWithStr));
                    }
                }
                
                if (ownerEmailIndex != -1 && !cursor.isNull(ownerEmailIndex)) {
                    reminder.setOwnerEmail(cursor.getString(ownerEmailIndex));
                }
                
                if (isSharedIndex != -1) {
                    reminder.setShared(cursor.getInt(isSharedIndex) == 1);
                }
            }
            cursor.close();
        }
        
        db.close();
        return reminder;
    }
    
    // Notes CRUD operations
    public long insertNote(Note note) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(KEY_NOTE_TITLE, note.getTitle());
        values.put(KEY_NOTE_CONTENT, note.getContent());
        values.put(KEY_NOTE_CREATED_AT, dateFormat.format(note.getCreatedAt()));
        values.put(KEY_NOTE_CREATED_BY, note.getCreatedBy());
        
        if (note.getSharedWith() != null && !note.getSharedWith().isEmpty()) {
            values.put(KEY_NOTE_SHARED_WITH, joinStrings(note.getSharedWith()));
        }
        
        long id = db.insert(TABLE_NOTES, null, values);
        db.close();
        return id;
    }
    
    public List<Note> getAllNotes() {
        List<Note> noteList = new ArrayList<>();
        String selectQuery = "SELECT * FROM " + TABLE_NOTES + " ORDER BY " + KEY_NOTE_CREATED_AT + " DESC";
        
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(selectQuery, null);
        
        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(KEY_NOTE_ID);
                int titleIndex = cursor.getColumnIndex(KEY_NOTE_TITLE);
                int contentIndex = cursor.getColumnIndex(KEY_NOTE_CONTENT);
                int createdAtIndex = cursor.getColumnIndex(KEY_NOTE_CREATED_AT);
                int createdByIndex = cursor.getColumnIndex(KEY_NOTE_CREATED_BY);
                int sharedWithIndex = cursor.getColumnIndex(KEY_NOTE_SHARED_WITH);
                
                if (idIndex != -1 && titleIndex != -1 && contentIndex != -1 && 
                    createdAtIndex != -1 && createdByIndex != -1) {
                    
                    Date createdAt = new Date();
                    try {
                        String dateStr = cursor.getString(createdAtIndex);
                        createdAt = dateFormat.parse(dateStr);
                    } catch (ParseException e) {
                        e.printStackTrace();
                    }
                    
                    Note note = new Note(
                            cursor.getLong(idIndex),
                            cursor.getString(titleIndex),
                            cursor.getString(contentIndex),
                            createdAt,
                            cursor.getString(createdByIndex)
                    );
                    
                    if (sharedWithIndex != -1 && !cursor.isNull(sharedWithIndex)) {
                        String sharedWithStr = cursor.getString(sharedWithIndex);
                        if (sharedWithStr != null && !sharedWithStr.isEmpty()) {
                            note.setSharedWith(splitString(sharedWithStr));
                        }
                    }
                    
                    noteList.add(note);
                }
            } while (cursor.moveToNext());
        }
        
        cursor.close();
        db.close();
        return noteList;
    }
    
    public List<Note> getNotesSharedWith(String email) {
        List<Note> sharedNoteList = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        
        String selectQuery = "SELECT * FROM " + TABLE_NOTES + 
                " WHERE " + KEY_NOTE_SHARED_WITH + " LIKE ? OR " + KEY_NOTE_CREATED_BY + " = ? " +
                " ORDER BY " + KEY_NOTE_CREATED_AT + " DESC";
        
        Cursor cursor = db.rawQuery(selectQuery, new String[]{"%" + email + "%", email});
        
        if (cursor.moveToFirst()) {
            do {
                int idIndex = cursor.getColumnIndex(KEY_NOTE_ID);
                int titleIndex = cursor.getColumnIndex(KEY_NOTE_TITLE);
                int contentIndex = cursor.getColumnIndex(KEY_NOTE_CONTENT);
                int createdAtIndex = cursor.getColumnIndex(KEY_NOTE_CREATED_AT);
                int createdByIndex = cursor.getColumnIndex(KEY_NOTE_CREATED_BY);
                
                if (idIndex != -1 && titleIndex != -1 && contentIndex != -1 && 
                    createdAtIndex != -1 && createdByIndex != -1) {
                    
                    Date createdAt = new Date();
                    try {
                        String dateStr = cursor.getString(createdAtIndex);
                        createdAt = dateFormat.parse(dateStr);
                    } catch (ParseException e) {
                        e.printStackTrace();
                    }
                    
                    Note note = new Note(
                            cursor.getLong(idIndex),
                            cursor.getString(titleIndex),
                            cursor.getString(contentIndex),
                            createdAt,
                            cursor.getString(createdByIndex)
                    );
                    
                    sharedNoteList.add(note);
                }
            } while (cursor.moveToNext());
        }
        
        cursor.close();
        db.close();
        return sharedNoteList;
    }
    
    // Helper methods for string lists
    private String joinStrings(List<String> strings) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < strings.size(); i++) {
            sb.append(strings.get(i));
            if (i < strings.size() - 1) {
                sb.append(",");
            }
        }
        return sb.toString();
    }
    
    private List<String> splitString(String joined) {
        return new ArrayList<>(Arrays.asList(joined.split(",")));
    }
}
