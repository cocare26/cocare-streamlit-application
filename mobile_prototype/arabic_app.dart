import 'package:flutter/material.dart';

void main() {
  runApp(const TelecomApp());
}

class TelecomApp extends StatelessWidget {
  const TelecomApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {

  final usernameController = TextEditingController();
  final passwordController = TextEditingController();

  String error = '';

  void login() {

    final value = usernameController.text;

    if (RegExp(r'^07[0-9]{8}$').hasMatch(value)) {

      setState(() {
        error = '';
      });

      print('Customer Login');

      // Navigator.push(...)

    } else if (RegExp(r'^[0-9]{11}$').hasMatch(value)) {

      setState(() {
        error = '';
      });

      print('Employee Login');

      // Navigator.push(...)

    } else {

      setState(() {
        error = 'رقم الهاتف أو الهوية غير صحيح';
      });

    }
  }

  @override
  Widget build(BuildContext context) {

    return Directionality(
      textDirection: TextDirection.rtl,

      child: Scaffold(

        backgroundColor: const Color(0xffeef3f6),

        body: Center(

          child: Container(

            width: 360,
            height: 660,

            decoration: BoxDecoration(

              borderRadius: BorderRadius.circular(42),

              gradient: const LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,

                colors: [
                  Color(0xffc9e7f7),
                  Color(0xffdff4ff),
                ],
              ),
            ),

            child: Stack(

              children: [

                Positioned(
                  top: 85,
                  left: 20,

                  child: Image.asset(
                    'assets/robot.png',
                    width: 145,
                  ),
                ),

                Positioned(
                  top: 200,
                  right: 58,

                  child: SizedBox(

                    width: 244,

                    child: Column(

                      children: [

                        TextField(

                          controller: usernameController,
                          keyboardType: TextInputType.number,

                          decoration: InputDecoration(

                            hintText: 'رقم الهاتف / رقم الهوية',

                            filled: true,
                            fillColor: Colors.white,

                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 18,
                            ),

                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(25),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),

                        const SizedBox(height: 13),

                        TextField(

                          controller: passwordController,
                          obscureText: true,

                          decoration: InputDecoration(

                            hintText: 'كلمة المرور',

                            filled: true,
                            fillColor: Colors.white,

                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 18,
                            ),

                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(25),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),

                        const SizedBox(height: 8),

                        TextButton(
                          onPressed: () {},

                          child: const Text(
                            'هل نسيت كلمة المرور؟',

                            style: TextStyle(
                              color: Colors.black54,
                              fontSize: 11,
                            ),
                          ),
                        ),

                        const SizedBox(height: 12),

                        SizedBox(

                          width: double.infinity,
                          height: 46,

                          child: ElevatedButton(

                            onPressed: login,

                            style: ElevatedButton.styleFrom(

                              backgroundColor: Colors.white,
                              foregroundColor: Colors.black,

                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(25),
                              ),
                            ),

                            child: const Text(

                              'تسجيل الدخول ›',

                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 10),

                        Text(

                          error,

                          style: const TextStyle(
                            color: Color(0xffc62828),
                            fontSize: 11,
                          ),
                        ),

                        const SizedBox(height: 15),

                        Row(

                          mainAxisAlignment: MainAxisAlignment.center,

                          children: [

                            const Text('👤 مستخدم جديد؟'),

                            GestureDetector(

                              onTap: () {},

                              child: const Text(

                                ' إنشاء حساب',

                                style: TextStyle(
                                  decoration: TextDecoration.underline,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
