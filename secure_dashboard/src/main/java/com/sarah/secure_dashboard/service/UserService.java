package com.sarah.secure_dashboard.service;

import com.sarah.secure_dashboard.model.User;
import com.sarah.secure_dashboard.repository.UserRepository;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;
    // private final PasswordEncoder passwordEncoder;

     public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
        // this.passwordEncoder = passwordEncoder;
    }

    public User register(User user) {

        user.setPassword(user.getPassword());
        user.setRole("ROLE_USER");

        return userRepository.save(user);
    }

   public User login(String username, String password) {

        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // TEMP: No password validation
        return user;
    }


}

