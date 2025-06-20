package com.example.smartreminder;

import android.content.Context;
import android.content.SharedPreferences;

public class AppSettings {
    private static final String PREF_NAME = "SmartReminderPrefs";
    private static final String KEY_APP_MODE = "app_mode";
    private static final String KEY_USER_EMAIL = "user_email";
    
    private static AppSettings instance;
    private final SharedPreferences prefs;
    private AppMode currentMode;
    private String userEmail;
    
    private AppSettings(Context context) {
        prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        String savedMode = prefs.getString(KEY_APP_MODE, AppMode.DEFAULT.name());
        currentMode = AppMode.valueOf(savedMode);
        userEmail = prefs.getString(KEY_USER_EMAIL, "");
    }
    
    public static synchronized AppSettings getInstance(Context context) {
        if (instance == null) {
            instance = new AppSettings(context.getApplicationContext());
        }
        return instance;
    }
    
    public AppMode getCurrentMode() {
        return currentMode;
    }
    
    public void setCurrentMode(AppMode mode) {
        this.currentMode = mode;
        prefs.edit().putString(KEY_APP_MODE, mode.name()).apply();
    }
    
    public String getUserEmail() {
        return userEmail;
    }
    
    public void setUserEmail(String email) {
        this.userEmail = email;
        prefs.edit().putString(KEY_USER_EMAIL, email).apply();
    }
    
    public boolean hasUserEmail() {
        return userEmail != null && !userEmail.isEmpty();
    }
}
