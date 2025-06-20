package com.example.smartreminder;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

public class RemindersFragment extends Fragment implements ReminderAdapter.ReminderClickListener {
    
    private RecyclerView recyclerView;
    private ReminderAdapter adapter;
    private List<Reminder> reminderList;
    private DatabaseHelper dbHelper;
    private TextView emptyView;
    
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_reminders, container, false);
        
        recyclerView = view.findViewById(R.id.reminders_recycler_view);
        emptyView = view.findViewById(R.id.empty_view);
        
        // Initialize database helper
        dbHelper = new DatabaseHelper(requireContext());
        
        // Initialize reminder list
        reminderList = new ArrayList<>();
        
        // Setup RecyclerView
        recyclerView.setLayoutManager(new LinearLayoutManager(requireContext()));
        adapter = new ReminderAdapter(reminderList, this);
        recyclerView.setAdapter(adapter);
        
        loadReminders();
        
        return view;
    }
    
    @Override
    public void onResume() {
        super.onResume();
        loadReminders();
    }
    
    private void loadReminders() {
        reminderList.clear();
        
        // Get user's own reminders
        reminderList.addAll(dbHelper.getAllReminders());
        
        // Also get reminders shared with the user
        String userEmail = AppSettings.getInstance(requireContext()).getUserEmail();
        if (!userEmail.isEmpty()) {
            reminderList.addAll(dbHelper.getRemindersSharedWith(userEmail));
        }
        
        if (reminderList.isEmpty()) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
        
        adapter.notifyDataSetChanged();
    }
    
    @Override
    public void onReminderClick(int position) {
        Reminder reminder = reminderList.get(position);
        // Handle reminder click - show details
    }
    
    @Override
    public void onShareClick(int position) {
        Reminder reminder = reminderList.get(position);
        showShareDialog(reminder);
    }
    
    private void showShareDialog(Reminder reminder) {
        // Implementation for sharing a reminder with other users
    }
}
