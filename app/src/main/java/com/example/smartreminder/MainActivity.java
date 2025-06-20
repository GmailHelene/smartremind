package com.example.smartreminder;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.viewpager2.widget.ViewPager2;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.tabs.TabLayout;
import com.google.android.material.tabs.TabLayoutMediator;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private ViewPager2 viewPager;
    private TabLayout tabLayout;
    private BottomNavigationView bottomNav;
    private FloatingActionButton fab;
    private DatabaseHelper dbHelper;
    private AppSettings appSettings;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize views
        viewPager = findViewById(R.id.viewPager);
        tabLayout = findViewById(R.id.tabLayout);
        bottomNav = findViewById(R.id.bottomNavigation);
        fab = findViewById(R.id.fab);
        
        // Initialize database helper
        dbHelper = new DatabaseHelper(this);
        
        // Initialize app settings
        appSettings = AppSettings.getInstance(this);
        
        // Setup user email if not set
        if (!appSettings.hasUserEmail()) {
            showEmailSetupDialog();
        }
        
        // Apply current app mode
        applyAppMode(appSettings.getCurrentMode());
        
        // Setup ViewPager with adapter
        setupViewPager();
        
        // Setup bottom navigation
        setupBottomNavigation();
        
        // Setup FAB
        fab.setOnClickListener(v -> {
            int currentItem = viewPager.getCurrentItem();
            if (currentItem == 0) {
                // Reminders tab
                showAddReminderDialog();
            } else {
                // Notes tab
                showAddNoteDialog();
            }
        });
    }
    
    private void setupViewPager() {
        MainPagerAdapter pagerAdapter = new MainPagerAdapter(this);
        viewPager.setAdapter(pagerAdapter);
        
        // Connect TabLayout with ViewPager2
        new TabLayoutMediator(tabLayout, viewPager, (tab, position) -> {
            switch (position) {
                case 0:
                    tab.setText("Reminders");
                    break;
                case 1:
                    tab.setText("Noteboard");
                    break;
            }
        }).attach();
    }
    
    private void setupBottomNavigation() {
        bottomNav.setOnItemSelectedListener(item -> {
            int itemId = item.getItemId();
            if (itemId == R.id.menu_home) {
                // Already on home screen
                return true;
            } else if (itemId == R.id.menu_settings) {
                openSettingsActivity();
                return true;
            } else if (itemId == R.id.menu_profile) {
                openProfileActivity();
                return true;
            }
            return false;
        });
    }
    
    private void showEmailSetupDialog() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_email_setup, null);
        EditText emailInput = dialogView.findViewById(R.id.email_input);
        
        new MaterialAlertDialogBuilder(this)
                .setTitle("Welcome to Smart Reminder")
                .setMessage("Please enter your email to enable sharing features")
                .setView(dialogView)
                .setCancelable(false)
                .setPositiveButton("Save", (dialog, which) -> {
                    String email = emailInput.getText().toString().trim();
                    if (isValidEmail(email)) {
                        appSettings.setUserEmail(email);
                        Toast.makeText(MainActivity.this, "Email saved", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this, "Please enter a valid email", Toast.LENGTH_SHORT).show();
                        showEmailSetupDialog(); // Show dialog again
                    }
                })
                .show();
    }
    
    private boolean isValidEmail(String email) {
        return email != null && android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches();
    }
    
    private void showAddReminderDialog() {
        Intent intent = new Intent(this, AddReminderActivity.class);
        startActivity(intent);
    }
    
    private void showAddNoteDialog() {
        Intent intent = new Intent(this, AddNoteActivity.class);
        startActivity(intent);
    }
    
    private void openSettingsActivity() {
        Intent intent = new Intent(this, SettingsActivity.class);
        startActivity(intent);
    }
    
    private void openProfileActivity() {
        Intent intent = new Intent(this, ProfileActivity.class);
        startActivity(intent);
    }
    
    private void applyAppMode(AppMode mode) {
        // Apply theme and behavior changes based on app mode
        switch (mode) {
            case ADHD_FRIENDLY:
                applyADHDFriendlyMode();
                break;
            case SILENT:
                applySilentMode();
                break;
            case DARK:
                applyDarkMode();
                break;
            case FOCUS:
                applyFocusMode();
                break;
            default:
                applyDefaultMode();
                break;
        }
    }
    
    private void applyADHDFriendlyMode() {
        // High contrast, simplified UI, visual cues
        // This would involve specific theme settings
        Toast.makeText(this, "ADHD-Friendly mode activated", Toast.LENGTH_SHORT).show();
    }
    
    private void applySilentMode() {
        // Disable sounds, vibrations and intrusive notifications
        Toast.makeText(this, "Silent mode activated", Toast.LENGTH_SHORT).show();
    }
    
    private void applyDarkMode() {
        // Apply dark theme
        Toast.makeText(this, "Dark mode activated", Toast.LENGTH_SHORT).show();
    }
    
    private void applyFocusMode() {
        // Simplified interface, block distractions
        Toast.makeText(this, "Focus mode activated", Toast.LENGTH_SHORT).show();
    }
    
    private void applyDefaultMode() {
        // Standard interface
        Toast.makeText(this, "Default mode activated", Toast.LENGTH_SHORT).show();
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_change_mode) {
            showModeSelectorDialog();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    
    private void showModeSelectorDialog() {
        String[] modes = new String[AppMode.values().length];
        for (int i = 0; i < AppMode.values().length; i++) {
            modes[i] = AppMode.values()[i].getDisplayName();
        }
        
        new MaterialAlertDialogBuilder(this)
                .setTitle("Select App Mode")
                .setItems(modes, (dialog, which) -> {
                    AppMode selectedMode = AppMode.values()[which];
                    appSettings.setCurrentMode(selectedMode);
                    applyAppMode(selectedMode);
                })
                .show();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Refresh data when returning to the activity
        if (viewPager.getAdapter() != null) {
            viewPager.getAdapter().notifyDataSetChanged();
        }
    }
    
    @Override
    protected void onDestroy() {
        dbHelper.close();
        super.onDestroy();
    }
}
