# CONTINUE.md: A Guide to the "wayfinder" Project

This document provides a comprehensive guide for developers working on the "wayfinder" project. It covers everything from getting started to the development workflow and key concepts.

## 1. Project Overview

**wayfinder** is a web-based application that appears to provide an IDE-like or file explorer interface.

- **Key Technologies:**
  - **React:** A JavaScript library for building user interfaces.
  - **Vite:** A fast build tool and development server for modern web projects.
  - **ESLint:** A tool for identifying and reporting on patterns found in ECMAScript/JavaScript code.

- **High-Level Architecture:**
  The project is a standard client-side React application. The architecture is component-based, with the main components located in the `src/components` directory. The `App.jsx` file serves as the main entry point for the application's UI, orchestrating the different components.

## 2. Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- [npm](https://www.npmjs.com/) (usually comes with Node.js)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd wayfinder
    ```
2.  **Install dependencies:**
    ```sh
    npm install
    ```

### Basic Usage

- **Running the development server:**
  ```sh
  npm run dev
  ```
  This will start the Vite development server, and you can view the application at `http://localhost:5173` (or another port if 5173 is in use).

- **Running tests:**
  (No test runner is configured yet. This section should be updated when a testing framework like Jest or Vitest is added.)

## 3. Project Structure

Here is an overview of the main directories and files in the project:

- **`.continue/rules/`**: Contains this guide. Continue.dev loads these files as context for the project.
- **`public/`**: Contains static assets that are not processed by the build tool.
- **`src/`**: The main source code directory.
  - **`src/assets/`**: Contains static assets like images and SVGs that are imported into components.
  - **`src/components/`**: Contains reusable React components.
    - `FileTree.jsx`: A component for displaying a file tree structure.
    - `Header.jsx`: The main header component for the application.
    - `IDE.jsx`: A component that seems to provide an IDE-like layout.
    - `Loading.jsx`: A loading indicator component.
  - **`src/App.jsx`**: The root component of the application.
  - **`src/main.jsx`**: The entry point for the React application.
- **`index.html`**: The main HTML file for the application.
- **`package.json`**: Lists the project's dependencies and scripts.
- **`vite.config.js`**: Configuration file for Vite.

## 4. Development Workflow

### Coding Standards

- The project uses **ESLint** to enforce code quality and consistency. Please ensure you have ESLint integrated into your editor.
- Follow the existing code style and conventions.

### Testing Approach

- Currently, there is no testing framework configured. When implemented, all new features should be accompanied by tests.

### Build and Deployment

- **Building for production:**
  ```sh
  npm run build
  ```
  This command creates a `dist` directory with the optimized, production-ready files.

### Contribution Guidelines

1.  Create a new branch for your feature or bug fix.
2.  Make your changes and ensure the code lints without errors (`npm run lint`).
3.  Commit your changes with a clear and descriptive message.
4.  Push your branch and open a pull request.

## 5. Key Concepts

- **Component-Based Architecture:** The UI is built using a hierarchy of React components.
- **Virtualization:** The use of `react-window` and `react-virtualized-auto-sizer` suggests that the application is designed to handle large lists of data (e.g., in the file tree) efficiently by only rendering the items visible on the screen.

## 6. Common Tasks

### Creating a New Component

1.  Create a new `.jsx` file in the `src/components/` directory (e.g., `MyComponent.jsx`).
2.  Write the component code.
3.  Import and use the new component in `App.jsx` or another relevant component.

## 7. Troubleshooting

- **Dependency issues:** If you encounter problems after pulling new changes, try deleting the `node_modules` directory and `package-lock.json`, then run `npm install` again.
- **Linting errors:** Run `npm run lint` to see a list of all linting issues in the project.

## 8. References

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Vite Documentation](https://vitejs.dev/guide/)
- [ESLint Documentation](https://eslint.org/docs/user-guide/)
