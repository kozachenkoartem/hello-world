#include <iostream>
#include <cstdlib>
#include <vector>
#include <memory>

using namespace std;


struct Animal {
	virtual void speak() {
		cout << "Я неведомое животное :(" << endl;
	}
};

struct Dog :public Animal {

	void speak() override {
		cout << "Гав, гав!!!" << endl;
	}
};


struct Fish :public Animal {

	void speak() override {
		cout << "Буль буль!!!" << endl;
	}
};


struct Cat :public Animal {

	void speak() override {
		cout << "Мяу!!!" << endl;
	}
};

struct Human :public Animal {

	void speak() override {
		cout << "Я человек !!!" << endl;
	}
};



Animal *get_random_animal() {
	static vector<shared_ptr<Animal>> animals = {
		shared_ptr<Animal>(new Animal()),
		shared_ptr<Animal>(new Dog()),
		shared_ptr<Animal>(new Cat()),
		shared_ptr<Animal>(new Human()),
		shared_ptr<Animal>(new Fish()),
	};
	return animals.at(rand() % 5).get();
}




int main()
{
	Animal animal;
	Dog dog;
	Human man;
	Fish fish;
	Cat cat;

	dog.speak();
	man.speak();

	cout << "+++++++++++++++++++++++++++++++++" << endl;
	Animal *a = &animal;

	a->speak();

	a = &man;
	a->speak();

	a = &fish;
	a->speak();


	cout << "+++++++++++++++++++++++++++++++++" << endl;

	for(auto i = 0; i < 10; i++){
		get_random_animal()->speak();
	}

	return 0;
}
