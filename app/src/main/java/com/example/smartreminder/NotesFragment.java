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

public class NotesFragment extends Fragment implements NoteAdapter.NoteClickListener {
    
    private RecyclerView recyclerView;
    private NoteAdapter adapter;
    private List<Note> noteList;
    private DatabaseHelper dbHelper;
    private TextView emptyView;
    
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_notes, container, false);
        
        recyclerView = view.findViewById(R.id.notes_recycler_view);
        emptyView = view.findViewById(R.id.empty_view);
        
        // Initialize database helper
        dbHelper = new DatabaseHelper(requireContext());
        
        // Initialize note list
        noteList = new ArrayList<>();
        
        // Setup RecyclerView
        recyclerView.setLayoutManager(new LinearLayoutManager(requireContext()));
        adapter = new NoteAdapter(noteList, this);
        recyclerView.setAdapter(adapter);
        
        loadNotes();
        
        return view;
    }
    
    @Override
    public void onResume() {
        super.onResume();
        loadNotes();
    }
    
    private void loadNotes() {
        noteList.clear();
        
        // Get notes accessible to the user
        String userEmail = AppSettings.getInstance(requireContext()).getUserEmail();
        if (!userEmail.isEmpty()) {
            noteList.addAll(dbHelper.getNotesSharedWith(userEmail));
        }
        
        if (noteList.isEmpty()) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
        
        adapter.notifyDataSetChanged();
    }
    
    @Override
    public void onNoteClick(int position) {
        Note note = noteList.get(position);
        // Handle note click - show details
    }
    
    @Override
    public void onShareClick(int position) {
        Note note = noteList.get(position);
        showShareDialog(note);
    }
    
    private void showShareDialog(Note note) {
        // Implementation for sharing a note with other users
    }
}
