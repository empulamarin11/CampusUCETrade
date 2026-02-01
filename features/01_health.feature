Feature: Healthcheck del sistema

  Scenario Outline: El servicio responde por /health a través del gateway
    Given tengo la URL base
    When hago un GET a "<path>"
    Then la respuesta debe ser 200

    Examples:
      | path                  |
      | /auth/health          |
      | /users/health         |
      | /items/health         |
      | /search/health        |
      | /reservations/health  |
      | /notifications/health |
      | /delivery/health      |
      | /reputation/health    |
      | /traceability/health  |
      | /chat/health          |
