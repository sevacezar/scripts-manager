import { useState, FormEvent, ChangeEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import type { ApiError } from '../types/api';

const Register = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { register: handleRegister } = useAuth();
  const navigate = useNavigate();

  // Validate login: letters, numbers, "-", "_", length 3-50
  const validateLogin = (value: string): string | null => {
    if (value.length === 0) {
      return null; // Don't show error for empty field
    }
    if (value.length < 3) {
      return 'Логин должен содержать не менее 3 символов';
    }
    if (value.length > 50) {
      return 'Логин должен содержать не более 50 символов';
    }
    const loginRegex = /^[a-zA-Z0-9_-]+$/;
    if (!loginRegex.test(value)) {
      return 'Логин может содержать только буквы, цифры, "-" и "_"';
    }
    return null;
  };

  // Validate password: minimum 8 characters
  const validatePassword = (value: string): string | null => {
    if (value.length === 0) {
      return null; // Don't show error for empty field
    }
    if (value.length < 8) {
      return 'Пароль должен содержать не менее 8 символов';
    }
    return null;
  };

  const handleLoginChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLogin(value);
    setLoginError(validateLogin(value));
    setError(null); // Clear general error when user starts typing
  };

  const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    setPasswordError(validatePassword(value));
    setError(null); // Clear general error when user starts typing
    
    // Re-validate confirm password if it's already filled
    if (confirmPassword) {
      setConfirmPasswordError(
        value !== confirmPassword ? 'Пароли не совпадают' : null
      );
    }
  };

  const handleConfirmPasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setConfirmPassword(value);
    setConfirmPasswordError(
      value !== password ? 'Passwords do not match' : null
    );
    setError(null); // Clear general error when user starts typing
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate all fields
    const loginValidationError = validateLogin(login);
    const passwordValidationError = validatePassword(password);
    const confirmPasswordValidationError = password !== confirmPassword 
      ? 'Passwords do not match' 
      : null;

    setLoginError(loginValidationError);
    setPasswordError(passwordValidationError);
    setConfirmPasswordError(confirmPasswordValidationError);

    if (loginValidationError || passwordValidationError || confirmPasswordValidationError) {
      return;
    }

    setIsLoading(true);

    try {
      await handleRegister({ login, password });
      // Registration successful - redirect to login page immediately
      navigate('/login');
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.message || 'Ошибка регистрации';
      
      // Check if user already exists (various possible error messages)
      const lowerMessage = errorMessage.toLowerCase();
      if (lowerMessage.includes('already exists') || 
          lowerMessage.includes('user with login') ||
          lowerMessage.includes('already exist') ||
          lowerMessage.includes('уже существует') ||
          lowerMessage.includes('пользователь с логином')) {
        setError(`Пользователь с логином "${login}" уже существует. Выберите другой логин.`);
      } else {
        setError(errorMessage);
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-primary">
            Создание аккаунта
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="login" className="block text-sm font-medium text-gray-700">
                Логин
              </label>
              <input
                id="login"
                name="login"
                type="text"
                required
                value={login}
                onChange={handleLoginChange}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary ${
                  loginError ? 'border-red-300' : 'border-gray-300'
                }`}
                aria-label="Login input"
                aria-invalid={!!loginError}
                aria-describedby={loginError ? 'login-error login-help' : 'login-help'}
              />
              {loginError && (
                <p id="login-error" className="mt-1 text-sm text-red-600" role="alert">
                  {loginError}
                </p>
              )}
              <p id="login-help" className="mt-1 text-xs text-gray-500">
                Логин должен содержать 3-50 символов и может содержать только буквы, цифры, "-" и "_"
              </p>
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={handlePasswordChange}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary ${
                  passwordError ? 'border-red-300' : 'border-gray-300'
                }`}
                aria-label="Password input"
                aria-invalid={!!passwordError}
                aria-describedby={passwordError ? 'password-error password-help' : 'password-help'}
              />
              {passwordError && (
                <p id="password-error" className="mt-1 text-sm text-red-600" role="alert">
                  {passwordError}
                </p>
              )}
              <p id="password-help" className="mt-1 text-xs text-gray-500">
                Пароль должен содержать не менее 8 символов
              </p>
            </div>
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Подтверждение пароля
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={handleConfirmPasswordChange}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary ${
                  confirmPasswordError ? 'border-red-300' : 'border-gray-300'
                }`}
                aria-label="Confirm password input"
                aria-invalid={!!confirmPasswordError}
                aria-describedby={confirmPasswordError ? 'confirm-password-error' : undefined}
              />
              {confirmPasswordError && (
                <p id="confirm-password-error" className="mt-1 text-sm text-red-600" role="alert">
                  {confirmPasswordError}
                </p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Register button"
            >
              {isLoading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
            </button>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Уже есть аккаунт?{' '}
              <Link
                to="/login"
                className="font-medium text-primary hover:text-primary-dark"
                tabIndex={0}
              >
                Войти
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;

