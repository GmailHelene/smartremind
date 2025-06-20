package com.example.smartreminder;

public enum AppMode {
    DEFAULT("Default"),
    ADHD_FRIENDLY("ADHD-Friendly"),
    SILENT("Silent Mode"),
    FOCUS("Focus Mode"),
    DARK("Dark Mode");
    
    private final String displayName;
    
    AppMode(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}
