# CO_O2_Analyser Documentation

This directory contains the documentation for the CO_O2_Analyser project.

## Structure

- `api/` - API documentation
- `user_guide/` - User manual and guides
- `developer/` - Developer documentation
- `examples/` - Code examples and tutorials

## Building Documentation

To build the documentation:

```bash
# Install documentation dependencies
pip install -r requirements-dev.txt

# Build HTML documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## Documentation Standards

- Use Markdown format for all documentation
- Follow the Google docstring style for Python code
- Include code examples where appropriate
- Keep documentation up to date with code changes

## Contributing

When adding new features or changing existing functionality:

1. Update relevant documentation
2. Add or update examples
3. Update API documentation if applicable
4. Test documentation builds successfully
