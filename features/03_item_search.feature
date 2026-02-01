Feature: Publicación y búsqueda de items

  Scenario: Crear un item y luego buscarlo
    Given tengo la URL base
    And genero un usuario de prueba
    And registro el usuario de prueba
    And inicio sesión y guardo el token
    And tengo el header Authorization listo
    And genero un nombre de item de prueba

    When hago un POST autenticado a "/items/" con JSON:
      """
      {
        "title": "{{item_title}}",
        "price": 250,
        "currency": "USD",
        "description": "Item de prueba para BDD"
      }
      """
    Then la respuesta debe ser uno de 200, 201

    When hago un GET a "/search/?q={{item_title}}"
    Then la respuesta debe ser 200

  Scenario: No se puede crear un item sin token
    Given tengo la URL base
    And genero un nombre de item de prueba
    When hago un POST a "/items/" con JSON:
      """
      {
        "title": "{{item_title}}",
        "price": 100,
        "currency": "USD",
        "description": "Intento sin token"
      }
      """
    Then la respuesta debe ser uno de 401, 403