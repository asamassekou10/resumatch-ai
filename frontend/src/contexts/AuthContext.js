import React, { createContext, useContext, useReducer, useEffect } from 'react';
import ApiService from '../services/api';
import config from '../config';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
  UPDATE_USER: 'UPDATE_USER'
};

// Reducer function
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem(config.storage.token);
        const userData = localStorage.getItem(config.storage.user);
        
        if (token && userData) {
          // Verify token is still valid
          JSON.parse(userData); // Validate JSON structure
          
          // Optionally verify with server
          try {
            const response = await ApiService.getCurrentUser();
            dispatch({
              type: AUTH_ACTIONS.LOGIN_SUCCESS,
              payload: {
                user: response.data.user,
                token
              }
            });
          } catch (error) {
            // Token is invalid, clear storage
            localStorage.removeItem(config.storage.token);
            localStorage.removeItem(config.storage.user);
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await ApiService.login(email, password);
      
      if (response.status === 'success') {
        const { user, access_token } = response.data;
        
        // Store in localStorage
        localStorage.setItem(config.storage.token, access_token);
        localStorage.setItem(config.storage.user, JSON.stringify(user));
        
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user, token: access_token }
        });
        
        return { success: true };
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.message || 'Login failed';
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage
      });
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (email, password) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });
    
    try {
      const response = await ApiService.register(email, password);
      
      if (response.status === 'success') {
        const { user, access_token } = response.data;
        
        // Store in localStorage
        localStorage.setItem(config.storage.token, access_token);
        localStorage.setItem(config.storage.user, JSON.stringify(user));
        
        dispatch({
          type: AUTH_ACTIONS.REGISTER_SUCCESS,
          payload: { user, token: access_token }
        });
        
        return { success: true };
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.message || 'Registration failed';
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: errorMessage
      });
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await ApiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear localStorage
      localStorage.removeItem(config.storage.token);
      localStorage.removeItem(config.storage.user);
      
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Change password function
  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await ApiService.changePassword(currentPassword, newPassword);
      
      if (response.status === 'success') {
        return { success: true };
      } else {
        throw new Error(response.message || 'Password change failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.message || 'Password change failed';
      return { success: false, error: errorMessage };
    }
  };

  // Update user function
  const updateUser = (userData) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_USER,
      payload: userData
    });
    
    // Update localStorage
    const updatedUser = { ...state.user, ...userData };
    localStorage.setItem(config.storage.user, JSON.stringify(updatedUser));
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Refresh user data from server
  const refreshUser = async () => {
    try {
      const response = await ApiService.getCurrentUser();
      if (response.data?.user) {
        dispatch({
          type: AUTH_ACTIONS.UPDATE_USER,
          payload: response.data.user
        });
        localStorage.setItem(config.storage.user, JSON.stringify(response.data.user));
        return response.data.user;
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
    return null;
  };

  // Check if user has an active weekly pass
  const hasActivePass = () => {
    if (!state.user?.weekly_pass) return false;
    return state.user.weekly_pass.is_active === true;
  };

  // Get pass expiration info
  const getPassInfo = () => {
    if (!state.user?.weekly_pass) return null;
    return state.user.weekly_pass;
  };

  // Check if user can perform analysis (has pass, credits, or subscription)
  const canAnalyze = () => {
    if (!state.user) return false;
    // Admin bypass
    if (state.user.is_admin) return true;
    // Has active weekly pass
    if (hasActivePass()) return true;
    // Has credits
    if (state.user.credits > 0) return true;
    // Has active subscription
    if (state.user.subscription_status === 'active') return true;
    return false;
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    changePassword,
    updateUser,
    clearError,
    refreshUser,
    hasActivePass,
    getPassInfo,
    canAnalyze
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

// Higher-order component for protected routes
export const withAuth = (WrappedComponent) => {
  return function ProtectedComponent(props) {
    const { isAuthenticated, isLoading } = useAuth();
    
    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-500"></div>
        </div>
      );
    }
    
    if (!isAuthenticated) {
      window.location.href = '/login';
      return null;
    }
    
    return <WrappedComponent {...props} />;
  };
};

export default AuthContext;
