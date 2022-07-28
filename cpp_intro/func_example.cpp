#include <iostream>

using namespace std;


enum class Animal {
	Dog,
	Fish,
	Cat,
	Human
};


void speak(Animal a) {

	if(a == Animal::Dog)
	{
		cout << "Гав, гав!!!" << endl;
	}
	else if(a == Animal::Fish)
	{
		cout << "Буль буль!!!" << endl;
	}
	else if(a == Animal::Cat)
	{
		cout << "Мяу!!!" << endl;
	}
	else
	{
		cout << "Привет, я Акакий!!!" << endl;
	}
}


int main()
{
	Animal dog = Animal::Dog;
	speak(dog);

	speak(Animal::Human);
	return 0;
}
