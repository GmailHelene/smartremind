package com.example.smartreminder;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.viewpager2.adapter.FragmentStateAdapter;

public class MainPagerAdapter extends FragmentStateAdapter {
    
    public MainPagerAdapter(@NonNull FragmentActivity fragmentActivity) {
        super(fragmentActivity);
    }
    
    @NonNull
    @Override
    public Fragment createFragment(int position) {
        switch (position) {
            case 0:
                return new RemindersFragment();
            case 1:
                return new NotesFragment();
            default:
                return new RemindersFragment();
        }
    }
    
    @Override
    public int getItemCount() {
        return 2; // Number of tabs
    }
}
