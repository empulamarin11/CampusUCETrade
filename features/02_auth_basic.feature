Feature: Autenticación básica (Registro y Login)

  Scenario: Registro de usuario exitoso
    Given tengo la URL base
    And genero un usuario de prueba
    When hago un POST a "/users/register" con JSON:
      """
      {
        "email": "{{email}}",
        "password": "Test1234*",
        "full_name": "Usuario BDD"
      }
      """
    Then la respuesta debe ser 200

  Scenario: Login exitoso con credenciales válidas
    Given tengo la URL base
    And genero un usuario de prueba
    And registro el usuario de prueba
    When hago un POST a "/auth/login" con JSON:
      """
      {
        "email": "{{email}}",
        "password": "Test1234*"
      }
      """
    Then la respuesta debe ser 200

  Scenario: Registro rechaza correo no institucional
    Given tengo la URL base
    When hago un POST a "/users/register" con JSON:
      """
      {
        "email": "noinst@test.com",
        "password": "Test1234*",
        "full_name": "Usuario No UCE"
      }
      """
    Then la respuesta debe ser 400
