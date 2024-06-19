import React, { useState } from 'react';
import { Form, Input, Button, notification } from 'antd';
import '../Login.css';

const Login = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(values);
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      notification.error({
        message: 'Вход не выполнен',
        description: 'Неверное имя пользователя или пароль',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Form name="login" onFinish={onFinish} className="login-form">
        <Form.Item
          name="username"
          rules={[{ required: true, message: 'Пожалуйста, введите имя пользователя!' }]}
        >
          <Input placeholder="Имя пользователя" />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
        >
          <Input.Password placeholder="Пароль" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} className="login-form-button">
            Войти
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Login;
