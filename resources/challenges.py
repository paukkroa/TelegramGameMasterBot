# Maybe at some point let users choose the difficulty?

# easy or fast
challenges_easy = [
    {
        'name': 'Take 2 swigs',
        'swigs': 2,
        'shots': 0,
        'points': 1
    },
    {
        'name': 'Take 3 swigs',
        'swigs': 3,
        'shots': 0,
        'points': 1
    },
{
        'name': 'Take 5 swigs',
        'swigs': 5,
        'shots': 0,
        'points': 1
    },
    {
        'name': 'Give out 5 swigs',
        'swigs': 0,
        'shots': 0,
        'points': 1
    },
    {
        'name': 'Tell a joke',
        'swigs': 0,
        'shots': 0,
        'points': 1
    }
]

challenges_medium = [
    {
        'name': 'Take 10 swigs',
        'swigs': 10,
        'shots': 0,
        'points': 3
    },
    {
        'name': 'Give out 10 swigs',
        'swigs': 0,
        'shots': 0,
        'points': 3
    },
    {
        'name': 'Decide a subgroup to take 6 swigs each',
        'swigs': 0,
        'shots': 0,
        'points': 3
    },
    {
        'name': 'Ever never I have?',
        'swigs': 0,
        'shots': 0,
        'points': 3
    },
    {
        'name': 'Do 10 push-ups',
        'swigs': 0,
        'shots': 0,
        'points': 3
    }
]

challenges_hard = [
    {
        'name': 'Give out a shot',
        'swigs': 0,
        'shots': 0,
        'points': 5
    },
    {
        'name': 'Take a shot',
        'swigs': 0,
        'shots': 1,
        'points': 5
    },
    {
        'name': 'Hug a tree for 40 seconds',
        'swigs': 0,
        'shots': 0,
        'points': 5
    },
    {
        'name': 'Get a cocktail made for you (bad)',
        'swigs': 16,
        'shots': 0,
        'points': 5
    }
]

all_challenges_by_level = [challenges_easy, challenges_medium, challenges_hard]
all_challenges = challenges_easy + challenges_medium + challenges_hard
