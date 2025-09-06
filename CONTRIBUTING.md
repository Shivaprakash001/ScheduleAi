# Contributing to ScheduleAI

Thank you for your interest in contributing to ScheduleAI! We welcome contributions from the community. This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/Shivaprakash001/ScheduleAi.git
   cd ScheduleAi
   ```
3. **Set up** the development environment:
   ```bash
   pip install -r requirements.txt
   # or
   uv sync
   ```
4. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. **Make** your changes and test them
6. **Commit** your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Create** a Pull Request on GitHub

## 🧪 Testing

Before submitting your changes, please ensure:

1. **Run the example script** to verify basic functionality:
   ```bash
   python example.py
   ```

2. **Test with different datasets** to ensure robustness

3. **Check for conflicts** in the generated schedules

4. **Verify visualizations** are generated correctly

## 📝 Code Style

We follow these coding standards:

- **Python Version**: Python 3.12+
- **Formatting**: Use consistent indentation (4 spaces)
- **Naming**: Use descriptive variable/function names
- **Documentation**: Add docstrings to all functions and classes
- **Type Hints**: Include type annotations where possible

### Example Function Documentation

```python
def generate_timetable(courses: List[Dict], rooms: List[Dict],
                      days: List[str], slots_per_day: int) -> Dict:
    """
    Generate an optimized timetable using hybrid approach.

    Args:
        courses: List of course dictionaries with scheduling requirements
        rooms: List of room dictionaries with capacity information
        days: List of day names for the schedule
        slots_per_day: Number of time slots per day

    Returns:
        Dictionary containing the generated schedule and metadata

    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If solver fails to find a feasible solution
    """
```

## 🐛 Reporting Issues

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Step-by-step instructions
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, dependencies
6. **Sample data**: If possible, include sample input data

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly
3. **Explain the use case** and benefits
4. **Consider implementation** complexity

## 🔧 Development Setup

For advanced development:

```bash
# Install development dependencies
pip install black isort flake8 mypy pytest

# Format code
black .
isort .

# Run linting
flake8 .

# Run type checking
mypy .

# Run tests
pytest
```

## 📚 Documentation

When adding new features:

1. **Update README.md** with usage examples
2. **Add docstrings** to all new functions
3. **Update this CONTRIBUTING.md** if needed
4. **Create examples** for complex features

## 🎯 Areas for Contribution

### High Priority
- **Performance optimization** for large datasets
- **Additional constraint types** (e.g., faculty preferences)
- **Web interface** for easier configuration
- **Database integration** for persistent storage

### Medium Priority
- **More visualization options** (calendars, Gantt charts)
- **Export formats** (PDF, JSON, CSV)
- **Configuration file support** (YAML, TOML)
- **Plugin system** for custom constraints

### Low Priority
- **Mobile app** interface
- **Cloud deployment** options
- **Multi-language support**
- **Integration with LMS** (Canvas, Moodle, etc.)

## 📄 License

By contributing to ScheduleAI, you agree that your contributions will be licensed under the same MIT License that covers the project.

## 🙋 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: spchidiri2006@gmail.com

## 🎉 Recognition

Contributors will be:
- Listed in the README.md contributors section
- Mentioned in release notes
- Recognized for significant contributions

Thank you for contributing to ScheduleAI! 🚀
