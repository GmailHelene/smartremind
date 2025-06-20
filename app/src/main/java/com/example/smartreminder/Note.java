package com.example.smartreminder;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class Note {
    private long id;
    private String title;
    private String content;
    private Date createdAt;
    private String createdBy;
    private List<String> sharedWith;
    
    public Note(long id, String title, String content, Date createdAt, String createdBy) {
        this.id = id;
        this.title = title;
        this.content = content;
        this.createdAt = createdAt;
        this.createdBy = createdBy;
        this.sharedWith = new ArrayList<>();
    }
    
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
    
    public String getContent() {
        return content;
    }
    
    public void setContent(String content) {
        this.content = content;
    }
    
    public Date getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
    
    public String getCreatedBy() {
        return createdBy;
    }
    
    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }
    
    public List<String> getSharedWith() {
        return sharedWith;
    }
    
    public void setSharedWith(List<String> sharedWith) {
        this.sharedWith = sharedWith;
    }
    
    public void addSharedUser(String email) {
        if (!sharedWith.contains(email)) {
            sharedWith.add(email);
        }
    }
}
