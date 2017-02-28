
Feature: expect-troop
    Expect troops to greet them appropriately

Scenario: Bomb hostiles about to arrive to neighbor

    Given the factories
        | Name       | Owner | Cyborgs |
        | My base    | ME    | 100     |
        | Neighbor   | ENEMY | 0       |
        | Enemy base | ENEMY | 0       |

    And the factory distance matrix of
        | 0 | 1 | 8 |
        | 1 | 0 | 8 |
        | 8 | 8 | 0 |
    
    And troops marching
        | Owner | To       | Count | Turns left |
        | ENEMY | Neighbor | 2     | 1          |

    When considering bombing

    Then a bomb should be dispatched from 'My base' to 'Neighbor'

Scenario: Let hostiles march closer

