import javax.swing.*;
import java.awt.*;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.HashMap;
public class HabitTrackerApp extends JFrame {
    private static final long serialVersionUID = 1L;
    private final DatabaseManager dbManager;
    private final User currentUser;
    private ArrayList<Habit> habits;
    private JComboBox<Habit> habitComboBox;
    private JButton[] calendarButtons;
    private JLabel streakLabel;
    private JLabel userLabel;
    private HashMap<LocalDate, Boolean> currentHabitLogs;
    private YearMonth currentMonth;
    private JLabel monthLabel;
    private JLabel yearLabel;
    public HabitTrackerApp(User user, DatabaseManager dbManager) {
        this.currentUser = user;
        this.dbManager = dbManager;
        habits = new ArrayList<>();
        currentHabitLogs = new HashMap<>();
        currentMonth = YearMonth.now();
        setTitle("Habit Tracker - " + user.getName());
        setSize(900, 650);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));
        add(createTopPanel(), BorderLayout.NORTH);
        add(createCenterPanel(), BorderLayout.CENTER);
        add(createBottomPanel(), BorderLayout.SOUTH);
        loadHabits();
        setVisible(true);
    }
    private JPanel createTopPanel() {
        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        topPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        userLabel = new JLabel("User: " + currentUser.getName() + " (@" + currentUser.getUsername() + ")");
        userLabel.setFont(new Font("Arial", Font.BOLD, 12));
        userLabel.setForeground(new Color(0, 100, 0));
        topPanel.add(userLabel);
        topPanel.add(Box.createHorizontalStrut(20));
        JLabel selectLabel = new JLabel("Select Habit:");
        topPanel.add(selectLabel);
        habitComboBox = new JComboBox<>();
        habitComboBox.setPreferredSize(new Dimension(200, 30));
        habitComboBox.addActionListener(e -> onHabitSelected());
        topPanel.add(habitComboBox);
        JButton newHabitButton = new JButton("New Habit");
        newHabitButton.addActionListener(e -> createNewHabit());
        topPanel.add(newHabitButton);
        JButton prevMonthButton = new JButton("< Prev Month");
        prevMonthButton.addActionListener(e -> changeMonth(-1));
        topPanel.add(prevMonthButton);
        JButton nextMonthButton = new JButton("Next Month >");
        nextMonthButton.addActionListener(e -> changeMonth(1));
        topPanel.add(nextMonthButton);
        JButton logoutButton = new JButton("Logout");
        logoutButton.addActionListener(e -> logout());
        topPanel.add(logoutButton);
        return topPanel;
    }
    private JPanel createCenterPanel() {
        JPanel centerPanel = new JPanel(new BorderLayout());
        centerPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        JPanel headerPanel = new JPanel(new BorderLayout());
        yearLabel = new JLabel(String.valueOf(currentMonth.getYear()), SwingConstants.CENTER);
        yearLabel.setFont(new Font("Arial", Font.BOLD, 24));
        headerPanel.add(yearLabel, BorderLayout.NORTH);
        monthLabel = new JLabel(currentMonth.getMonth().toString(), SwingConstants.CENTER);
        monthLabel.setFont(new Font("Arial", Font.BOLD, 18));
        headerPanel.add(monthLabel, BorderLayout.CENTER);
        centerPanel.add(headerPanel, BorderLayout.NORTH);
        JPanel calendarPanel = new JPanel(new GridLayout(7, 7, 5, 5));
        calendarButtons = new JButton[42];
        String[] dayNames = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
        for (String dayName : dayNames) {
            JLabel dayLabel = new JLabel(dayName, SwingConstants.CENTER);
            dayLabel.setFont(new Font("Arial", Font.BOLD, 16));
            calendarPanel.add(dayLabel);
        }
        for (int i = 0; i < 42; i++) {
            final int index = i;
            JButton dayButton = new JButton("");
            dayButton.setPreferredSize(new Dimension(80, 60));
            dayButton.setFont(new Font("Arial", Font.BOLD, 16));
            dayButton.setOpaque(true);
            dayButton.setBorderPainted(true);
            dayButton.setBackground(Color.LIGHT_GRAY);
            dayButton.addActionListener(e -> onDayClicked(index));
            calendarButtons[i] = dayButton;
            calendarPanel.add(dayButton);
        }
        centerPanel.add(calendarPanel, BorderLayout.CENTER);
        return centerPanel;
    }
    private JPanel createBottomPanel() {
        JPanel bottomPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        bottomPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        streakLabel = new JLabel("Current Streak: 0 days");
        streakLabel.setFont(new Font("Arial", Font.BOLD, 14));
        bottomPanel.add(streakLabel);
        bottomPanel.add(Box.createHorizontalStrut(50));
        JButton exportButton = new JButton("Export Report");
        exportButton.addActionListener(e -> exportReport());
        bottomPanel.add(exportButton);
        return bottomPanel;
    }
    private void loadHabits() {
        habits = dbManager.getHabitsForUser(currentUser.getId());
        habitComboBox.removeAllItems();
        for (Habit habit : habits) {
            habitComboBox.addItem(habit);
        }
        if (!habits.isEmpty()) {
            habitComboBox.setSelectedIndex(0);
            onHabitSelected();
        }
    }
    private void onHabitSelected() {
        Habit selectedHabit = (Habit) habitComboBox.getSelectedItem();
        if (selectedHabit != null) {
            currentHabitLogs = dbManager.getLogsForHabit(selectedHabit.getId());
            updateCalendar();
            updateStreak();
        }
    }
    private void updateCalendar() {
        LocalDate firstOfMonth = currentMonth.atDay(1);
        int daysInMonth = currentMonth.lengthOfMonth();
        int firstDayOfWeek = firstOfMonth.getDayOfWeek().getValue() % 7;
        LocalDate today = LocalDate.now();
        yearLabel.setText(String.valueOf(currentMonth.getYear()));
        monthLabel.setText(currentMonth.getMonth().toString());
        for (int i = 0; i < 42; i++) {
            calendarButtons[i].setText("");
            calendarButtons[i].setBackground(Color.LIGHT_GRAY);
            calendarButtons[i].setEnabled(false);
        }
        for (int day = 1; day <= daysInMonth; day++) {
            int buttonIndex = firstDayOfWeek + day - 1;
            if (buttonIndex < 42) {
                calendarButtons[buttonIndex].setText(String.valueOf(day));
                LocalDate date = currentMonth.atDay(day);
                if (date.isBefore(today)) {
                    calendarButtons[buttonIndex].setEnabled(false);
                    calendarButtons[buttonIndex].setToolTipText("Past dates cannot be edited");
                } else {
                    calendarButtons[buttonIndex].setEnabled(true);
                    calendarButtons[buttonIndex].setToolTipText("Click to toggle completion");
                }
                if (currentHabitLogs.containsKey(date)) {
                    boolean completed = currentHabitLogs.get(date);
                    if (completed) {
                        calendarButtons[buttonIndex].setBackground(new Color(34, 197, 94));
                    } else {
                        calendarButtons[buttonIndex].setBackground(new Color(239, 68, 68));
                    }
                } else {
                    if (date.isBefore(today)) {
                        calendarButtons[buttonIndex].setBackground(new Color(200, 200, 200));
                    } else {
                        calendarButtons[buttonIndex].setBackground(Color.WHITE);
                    }
                }
            }
        }
    }
    private void onDayClicked(int buttonIndex) {
        Habit selectedHabit = (Habit) habitComboBox.getSelectedItem();
        if (selectedHabit == null) {
            JOptionPane.showMessageDialog(this, "Please select a habit first!");
            return;
        }
        String dayText = calendarButtons[buttonIndex].getText();
        if (dayText.isEmpty()) {
            return;
        }
        int day = Integer.parseInt(dayText);
        LocalDate date = currentMonth.atDay(day);
        Color currentColor = calendarButtons[buttonIndex].getBackground();
        if (currentColor.equals(Color.WHITE)) {
            dbManager.logHabit(selectedHabit.getId(), date, true);
            currentHabitLogs.put(date, true);
            calendarButtons[buttonIndex].setBackground(Color.GREEN);
        } else if (currentColor.equals(Color.GREEN)) {
            dbManager.logHabit(selectedHabit.getId(), date, false);
            currentHabitLogs.put(date, false);
            calendarButtons[buttonIndex].setBackground(Color.RED);
        } else if (currentColor.equals(Color.RED)) {
            dbManager.deleteHabitLog(selectedHabit.getId(), date);
            currentHabitLogs.remove(date);
            calendarButtons[buttonIndex].setBackground(Color.WHITE);
        }
        updateStreak();
    }
    private void createNewHabit() {
        String habitName = JOptionPane.showInputDialog(this, "Enter habit name:");
        if (habitName != null && !habitName.trim().isEmpty()) {
            int habitId = dbManager.addHabitForUser(habitName.trim(), currentUser.getId());
            if (habitId > 0) {
                JOptionPane.showMessageDialog(this, "Habit created successfully!");
                loadHabits();
            } else {
                JOptionPane.showMessageDialog(this, "Error creating habit!", "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }
    private void logout() {
        int confirm = JOptionPane.showConfirmDialog(this,
                "Are you sure you want to logout?",
                "Confirm Logout",
                JOptionPane.YES_NO_OPTION);
        if (confirm == JOptionPane.YES_OPTION) {
            dispose();
            SwingUtilities.invokeLater(() -> new LoginFrame());
        }
    }
    private void changeMonth(int offset) {
        currentMonth = currentMonth.plusMonths(offset);
        updateCalendar();
    }
    private void updateStreak() {
        int streak = 0;
        LocalDate today = LocalDate.now();
        Boolean todayStatus = currentHabitLogs.get(today);
        if (todayStatus != null && !todayStatus) {
            streakLabel.setText("Current Streak: 0 days");
            return;
        }
        LocalDate checkDate;
        if (todayStatus != null && todayStatus) {
            checkDate = today;
        } else {
            checkDate = today.minusDays(1);
        }
        while (currentHabitLogs.getOrDefault(checkDate, false)) {
            streak++;
            checkDate = checkDate.minusDays(1);
        }
        streakLabel.setText("Current Streak: " + streak + " days");
    }
    private void exportReport() {
        Habit selectedHabit = (Habit) habitComboBox.getSelectedItem();
        if (selectedHabit == null) {
            JOptionPane.showMessageDialog(this, "Please select a habit first!");
            return;
        }
        new Thread(() -> {
            try {
                IFileExporter exporter = new TxtFileExporter("habit_report.txt");
                exporter.export(selectedHabit.getName(), currentHabitLogs);
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, 
                        "Report exported successfully to habit_report.txt!", 
                        "Export Success", 
                        JOptionPane.INFORMATION_MESSAGE);
                });
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, 
                        "Error exporting report: " + e.getMessage(), 
                        "Export Error", 
                        JOptionPane.ERROR_MESSAGE);
                });
            }
        }).start();
    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new LoginFrame();
        });
    }
}