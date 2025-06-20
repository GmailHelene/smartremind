package com.example.smartreminder;

import java.util.ArrayList;
import java.util.List;

public class Reminder {
    private long id;
    private String title;
    private String description;
    private String date;
    private List<String> sharedWith;
    private String ownerEmail;
    private boolean isShared;
    
    public Reminder(long id, String title, String description, String date) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.date = date;
        this.sharedWith = new ArrayList<>();
        this.isShared = false;
    }

    // Additional constructor for shared reminders
    public Reminder(long id, String title, String description, String date, String ownerEmail, boolean isShared) {
        this(id, title, description, date);
        this.ownerEmail = ownerEmail;
        this.isShared = isShared;
    }
    
    // Getters and setters
    public long getId() {
        return id;
    }
    
    public void setId(long id) {
        this.id = id;
    }
    
    public String getTitle() {
        return title;
    }
    
    public void setTitle(String title) {
        this.title = title;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public String getDate() {
        return date;
    }
    
    public void setDate(String date) {
        this.date = date;
    }
    
    public List<String> getSharedWith() {
        return sharedWith;
    }
    
    public void setSharedWith(List<String> sharedWith) {
        this.sharedWith = sharedWith;
    }
    
    public void addSharedEmail(String email) {
        if (!sharedWith.contains(email)) {
            sharedWith.add(email);
        }
    }
    
    public String getOwnerEmail() {
        return ownerEmail;
    }
    
    public void setOwnerEmail(String ownerEmail) {
        this.ownerEmail = ownerEmail;
    }
    
    public boolean isShared() {
        return isShared;
    }
    
    public void setShared(boolean shared) {
        isShared = shared;
    }
}
