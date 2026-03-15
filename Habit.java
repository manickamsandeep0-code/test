public class Habit extends TrackerEvent {
    public Habit(int id, String name) {
        super(id, name);
    }
    @Override
    public String getDetails() {
        return "Habit: " + getName();
    }
    @Override
    public String toString() {
        return getName();
    }
}