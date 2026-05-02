# Chapter 4: Divide-and-Conquer

For the divide-and-conquer matrix-multiplication algorithms presented in Sections 4.1 and 4.2, we’ll derive recurrences that describe their worst-case running times. To understand why these two divide-and-conquer algorithms perform the way they do, you’ll need to learn how to solve the recurrences that describe their running times. Sections 4.3–4.7 teach several methods for solving recurrences. These sections also explore the mathematics behind recurrences, which can give you stronger intuition for designing your own divide-and-conquer algorithms.

We want to get to the algorithms as soon as possible. So, let’s just cover a few recurrence basics now, and then we’ll look more deeply at recurrences, especially how to solve them, after we see the matrix-multiplication examples.

The general form of a recurrence is an equation or inequality that describes a function over the integers or reals using the function itself. It contains two or more cases, depending on the argument. If a case involves the recursive invocation of the function on different (usually smaller) inputs, it is a recursive case. If a case does not involve a recursive invocation, it is a base case. There may be zero, one, or many functions that satisfy the statement of the recurrence. The recurrence is well defined if there is at least one function that satisfies it, and ill defined otherwise.

## Algorithmic recurrences

We’ll be particularly interested in recurrences that describe the running times of divide-and-conquer algorithms. A recurrence T .n/ is algorithmic if, for every sufficiently large threshold constant n0 >0, the following two properties hold:

1. For all n < n0, we have T .n/ D ‚.1/. 2. For all n  n0, every path of recursion terminates in a defined base case within a finite number of recursive invocations. Similar to how we sometimes abuse asymptotic notation (see page 60), when a function is not defined for all arguments, we understand that this deûnition is constrained to values of n for which T .n/ is defined.

Why would a recurrence T .n/ that represents a (correct) divide-and-conquer algorithm’s worst-case running time satisfy these properties for all sufficiently largethreshold constants? The ûrst property says that there exist constants c1; c2 such that 0< c1 හ T.n/ හc2 for n < n0. For every legal input, the algorithm must output the solution to the problem it’s solving in finite time (see Section 1.1). Thus we can let c1 be the minimum amount of time to call and return from a procedure, which must be positive, because machine instructions need to be executed to invoke a procedure. The running time of the algorithm may not be defined for some values of n if there are no legal inputs of that size, but it must be defined for at least one, or else the <algorithm= doesn’t solve any problem. Thus we can let c2 be the algorithm’s maximum running time on any input of size n < n0, where n0 is

sufficiently large that the algorithm solves at least one problem of size less than n0. The maximum is well defined, since there are at most a finite number of inputs of size less than n0, and there is at least one if n0 is sufficiently large. Consequently, T .n/ satisfies the ûrst property. If the second property fails to hold for T .n/, then the algorithm isn’t correct, because it would end up in an infinite recursive loop or otherwise fail to compute a solution. Thus, it stands to reason that a recurrence for the worst-case running time of a correct divide-and-conquer algorithm would be algorithmic.

## Conventions for recurrences

We adopt the following convention:

Whenever a recurrence is stated without an explicit base case, we assume

that the recurrence is algorithmic.

That means you’re free to pick any sufficiently large threshold constant n0 for the range of base cases where T .n/ D ‚.1/. Interestingly, the asymptotic solutions of

most algorithmic recurrences you’re likely to see when analyzing algorithms don’t depend on the choice of threshold constant, as long as it’s large enough to make the recurrence well defined.

Asymptotic solutions of algorithmic divide-and-conquer recurrences also don’t tend to change when we drop any üoors or ceilings in a recurrence defined on the integers to convert it to a recurrence defined on the reals. Section 4.7 gives a sufûcient condition for ignoring üoors and ceilings that applies to most of the divideand- conquer recurrences you’re likely to see. Consequently, we’ll frequently statealgorithmic recurrences without üoors and ceilings. Doing so generally simplifiesthe statement of the recurrences, as well as any math that we do with them.

You may sometimes see recurrences that are not equations, but rather inequalities, such as T .n/ හ 2T .n=2/ C ‚.n/. Because such a recurrence states only an upper bound on T .n/, we express its solution using O-notation rather than ‚-notation. Similarly, if the inequality is reversed to T .n/  2T .n=2/ C ‚.n/, then, because the recurrence gives only a lower bound on T .n/, we use Y-notation in its solution.

## Divide-and-conquer and recurrences

This chapter illustrates the divide-and-conquer method by presenting and using recurrences to analyze two divide-and-conquer algorithms for multiplying nn matrices. Section 4.1 presents a simple divide-and-conquer algorithm that solves a matrix-multiplication problem of size n by breaking it into four subproblems of size n=2, which it then solves recursively. The running time of the algorithm can be characterized by the recurrence

T .n/ D 8T .n=2/ C ‚.1/ ;

which turns out to have the solution T .n/ D ‚.n3/. Although this divide-andconquer algorithm is no faster than the straightforward method that uses a triply

nested loop, it leads to an asymptotically faster divide-and-conquer algorithm due to V. Strassen, which we’ll explore in Section 4.2. Strassen’s remarkable algorithm

divides a problem of size n into seven subproblems of size n=2 which it solves recursively. The running time of Strassen’s algorithm can be described by the recurrence

T .n/ D 7T .n=2/ C ‚.n2/ ;

which has the solution T .n/ D ‚.nlg7/ D O.n2:81/. Strassen’s algorithm beats the straightforward looping method asymptotically.

These two divide-and-conquer algorithms both break a problem of size n into several subproblems of size n=2. Although it is common when using divide-andconquer for all the subproblems to have the same size, that isn’t always the case. Sometimes it’s productive to divide a problem of size n into subproblems of different sizes, and then the recurrence describing the running time reüects the irregularity. For example, consider a divide-and-conquer algorithm that divides a problem of size n into one subproblem of size n=3 and another of size 2n=3, taking ‚.n/ time to divide the problem and combine the solutions to the subproblems. Then the algorithm’s running time can be described by the recurrence

T .n/ D T .n=3/ C T .2n=3/ C ‚.n/ ;

which turns out to have solution T .n/ D ‚.n lgn/. We’ll even see an algorithm in Chapter 9 that solves a problem of size n by recursively solving a subproblem of size n=5 and another of size 7n=10, taking ‚.n/ time for the divide and combine

steps. Its performance satisfies the recurrence

T .n/ D T .n=5/ C T .7n=10/ C ‚.n/ ;

which has solution T .n/ D ‚.n/.

Although divide-and-conquer algorithms usually create subproblems with sizes a constant fraction of the original problem size, that’s not always the case. For example, a recursive version of linear search (see Exercise 2.1-4) creates just onesubproblem, with one element less than the original problem. Each recursive call takes constant time plus the time to recursively solve a subproblem with one less element, leading to the recurrence

T.n/ D T.n 1/ C‚.1/ ;

which has solution T .n/ D ‚.n/. Nevertheless, the vast majority of efûcient divide-and-conquer algorithms solve subproblems that are a constant fraction of the size of the original problem, which is where we’ll focus our efforts.

Solving recurrences

After learning about divide-and-conquer algorithms for matrix multiplication in Sections 4.1 and 4.2, we’ll explore several mathematical tools for solving recurrences4that is, for obtaining asymptotic ‚-, O-, or Y-bounds on their solutions. We want simple-to-use tools that can handle the most commonly occurring situa

tions. But we also want general tools that work, perhaps with a little more effort, for less common cases. This chapter offers four methods for solving recurrences:



In the substitution method (Section 4.3), you guess the form of a bound and then use mathematical induction to prove your guess correct and solve for constants. This method is perhaps the most robust method for solving recurrences, but it also requires you to make a good guess and to produce an inductive proof.



The recursion-tree method (Section 4.4) models the recurrence as a tree whosenodes represent the costs incurred at various levels of the recursion. To solve the recurrence, you determine the costs at each level and add them up, perhapsusing techniques for bounding summations from Section A.2. Evenif you don’tuse thismethod toformally prove abound, itcanbehelpful inguessing theformof the bound for use in the substitution method.



The mastermethod (Sections 4.5and4.6)istheeasiest method, whenitapplies. It provides bounds for recurrences of the form

T.n/ D aT.n=b/ Cf.n/;

where a>0 and b>1 are constants and f .n/ is a given <driving= function. This type of recurrence tends to arise more frequently in the study of algorithmsthan any other. It characterizes a divide-and-conquer algorithm that creates a subproblems, each of which is 1=b times the size of the original problem, using f .n/ time for the divide and combine steps. To apply the master method, you need to memorize three cases, but once you do, you can easily determineasymptotic bounds on running times for many divide-and-conquer algorithms.



The Akra-Bazzi method (Section 4.7) is a general method for solving divideand- conquer recurrences. Although it involves calculus, it can be used to attack more complicated recurrences than those addressed by the master method.

## 4.1 Multiplying square matrices We can use the divide-and-conquer method to multiply square matrices. If you’ve seen matrices before, then you probably know how to multiply them. (Otherwise,

## 4.1 Multiplying square matrices 81 you should read Section D.1.) Let A D .aik/ and B D .bjk / be square nn matrices. The matrix product C D AB is also an nn matrix, where for i;j D 1;2;:::;n, the .i; j / entry of C is given by

n

X

cij D aik bkj : (4.1)

kD1

Generally, we’ll assume that the matrices are dense, meaning that most of the n2 entries are not 0, as opposed to sparse, where most of the n2 entries are 0 and the nonzero entries can be stored more compactly than in an nn array.

Computing the matrix C requires computing n2 matrix entries, each of which is the sum of n pairwise products of input elements from A and B. The MATRIXMULTIPLY procedure implements this strategy in a straightforward manner, and it generalizes the problem slightly. It takes as input three nn matrices A, B, and C , and it adds the matrix product AB to C , storing the result in C . Thus, it computes C D C CAB, instead of just C D AB. If only the product AB is needed, just initialize all n2 entries of C to 0 before calling the procedure, which takes an additional ‚.n2/ time. We’ll see that the cost of matrix multiplication asymptotically dominates this initialization cost.

MATRIX-MULTIPLY.A; B; C; n/

1 for i D1 to n // compute entries in each of n rows

2 for j D1 to n // compute n entries in row i

3 for kD1 to n

4 cij Dcij Caik bkj // add in another term of equation (4.1)

The pseudocode for MATRIX-MULTIPLY works as follows. The for loop of lines 134 computes the entries of each row i, and within a given row i, the for loop of lines 234 computes each of the entries cij for each column j . Each iteration of the for loop of lines 334 adds in one more term of equation (4.1).

Because each of the triply nested for loops runs for exactly n iterations, and each execution of line 4 takes constant time, the MATRIX-MULTIPLY procedure operates in ‚.n3/ time. Even if we add in the ‚.n2/ time for initializing C to 0, the running time is still ‚.n3/.

A simple divide-and-conquer algorithm

Let’s see how to compute the matrix product AB using divide-and-conquer. For

n>1, the divide step partitions the nn matrices into four n=2n=2 submatrices. We’ll assume that n is an exact power of 2, so that as the algorithm recurses, we are guaranteed that the submatrix dimensions are integer. (Exercise 4.1-1 asks you

to relax this assumption.) As with MATRIX-MULTIPLY, we’ll actually compute C D C CAB. But to simplify the math behind the algorithm, let’s assume that C has been initialized to the zero matrix, so that we are indeed computing C D AB.

The divide step views each of the nn matrices A, B, and C as four n=2  n=2 submatrices:

Î ÏÎ ÏÎÏ

A11 A12 B11 B12 C11 C12

AD ;BD ;CD: (4.2)

A21 A22 B21 B22 C21 C22

Then we can write the matrix product as

ÎÏÎ ÏÎ Ï

C11 C12 A11 A12 B11 B12

D (4.3)

C21 C22 A21 A22 B21 B22

ÎÏ

A11 B11 CA12 B21 A11 B12 CA12 B22

D; (4.4)

A21 B11 CA22 B21 A21 B12 CA22 B22

which corresponds to the equations

C11 D A11 B11 CA12 B21 ; (4.5) C12 D A11 B12 CA12 B22 ; (4.6) C21 D A21 B11 CA22 B21 ; (4.7) C22 D A21 B12 CA22 B22 : (4.8)

Equations (4.5)3(4.8) involve eight n=2  n=2 multiplications and four additions of n=2  n=2 submatrices.

As we look to transform these equations to an algorithm that can be described with pseudocode, or even implemented for real, there are two common approachesfor implementing the matrix partitioning.

One strategy is to allocate temporary storage to hold A’s four submatrices A11, A12, A21, and A22 and B’s four submatrices B11, B12, B21, and B22. Then copy each element in A and B toits corresponding location inthe appropriate submatrix. After the recursive conquer step, copy the elements in each of C ’s four submatrices C11, C12, C21, and C22 to their corresponding locations in C . This approach takes ‚.n2/ time, since 3n2 elements are copied.

The second approach uses index calculations and is faster and more practical. A submatrix can be speciûed within a matrix by indicating where within the matrix the submatrix lies without touching any matrix elements. Partitioning a matrix (or recursively, a submatrix) only involves arithmetic on this location information, which has constant size independent of the size of the matrix. Changes to the submatrix elements update the original matrix, since they occupy the same storage.

Going forward, we’ll assume that index calculations are used and that partitioning can be performed in ‚.1/ time. Exercise 4.1-3 asks you to show that it makesno difference to the overall asymptotic running time of matrix multiplication, however, whether the partitioning of matrices uses the ûrst method of copying or the

## 4.1 Multiplying square matrices 83 second method of index calculation. But for other divide-and-conquer matrix calculations, such as matrix addition, it can make a difference, as Exercise 4.1-4 asks you to show.

The procedure MATRIX-MULTIPLY-RECURSIVE uses equations (4.5)3(4.8) to implement a divide-and-conquer strategy for square-matrix multiplication. Like MATRIX-MULTIPLY, the procedure MATRIX-MULTIPLY-RECURSIVE computes C D C CAB since, if necessary, C can be initialized to 0 before the procedure is called in order to compute only C D AB.

MATRIX-MULTIPLY-RECURSIVE.A; B; C; n/

1 if n == 1

2 // Base case.

3 c11 Dc11 Ca11 b11

4 return

5 // Divide.

6 partition A, B, and C into n=2  n=2 submatrices

A11; A12; A21; A22; B11; B12; B21; B22;

and C11; C12; C21; C22; respectively

7 // Conquer.

8 MATRIX-MULTIPLY-RECURSIVE.A11; B11; C11; n=2/ 9 MATRIX-MULTIPLY-RECURSIVE.A11; B12; C12; n=2/ 10 MATRIX-MULTIPLY-RECURSIVE.A21; B11; C21; n=2/ 11 MATRIX-MULTIPLY-RECURSIVE.A21; B12; C22; n=2/ 12 MATRIX-MULTIPLY-RECURSIVE.A12; B21; C11; n=2/ 13 MATRIX-MULTIPLY-RECURSIVE.A12; B22; C12; n=2/ 14 MATRIX-MULTIPLY-RECURSIVE.A22; B21; C21; n=2/ 15 MATRIX-MULTIPLY-RECURSIVE.A22; B22; C22; n=2/

As we walk through the pseudocode, we’ll derive a recurrence to characterize its running time. Let T .n/ be the worst-case time to multiply two nn matrices using this procedure.

In the base case, when nD1, line 3 performs just the one scalar multiplication and one addition, which means that T .1/ D ‚.1/. As is our convention for constant base cases, we can omit this base case in the statement of the recurrence.

The recursive case occurs when n>1. As discussed, we’ll use index calculations to partition the matrices in line 6, taking ‚.1/ time. Lines 8315 recursively call MATRIX-MULTIPLY-RECURSIVE a total of eight times. The ûrst four recursive calls compute the ûrst terms of equations (4.5)3(4.8), and the subsequent four recursive calls compute and add in the second terms. Each recursive call adds the product of a submatrix of A and a submatrix of B to the appropriate submatrix

of C in place, thanks to index calculations. Because each recursive call multiplies two n=2  n=2 matrices, thereby contributing T .n=2/ to the overall running time, the time taken by all eight recursive calls is 8T .n=2/. There is no combine step, because the matrix C is updated in place. The total time for the recursive case, therefore, is the sum of the partitioning time and the time for all the recursive calls, or ‚.1/ C 8T .n=2/.

Thus, omitting the statement of the base case, our recurrence for the running time of MATRIX-MULTIPLY-RECURSIVE is T .n/ D 8T .n=2/ C ‚.1/ : (4.9) As we’ll see from the master method in Section 4.5, recurrence (4.9) has the solution T .n/ D ‚.n3/, which means that it has the same asymptotic running time asthe straightforward MATRIX-MULTIPLY procedure.

Why is the ‚.n3/ solution to this recurrence so much larger than the ‚.n lgn/ solution to the merge-sort recurrence (2.3) on page 41? After all, the recurrence for merge sort contains a ‚.n/ term, whereas the recurrence for recursive matrix multiplication contains only a ‚.1/ term.

Let’s think about what the recursion tree for recurrence (4.9) would look like as compared with the recursion tree for merge sort, illustrated in Figure 2.5 on page 43. The factor of 2 in the merge-sort recurrence determines how many children each tree node has, whichin turn determines how manytermscontribute tothesum at each level of the tree. In comparison, for the recurrence (4.9) for MATRIXMULTIPLY- RECURSIVE, each internal node intherecursion tree haseightchildren, not two, leading to a <bushier= recursion tree with many more leaves, despite the fact that the internal nodes are each much smaller. Consequently, the solution to

recurrence (4.9) grows much more quickly than the solution to recurrence (2.3),

which is borne out in the actual solutions: ‚.n3/ versus ‚.n lgn/.

## Exercises

Note: You may wish to read Section 4.5 before attempting some of these exercises.

4.1-1

Generalize MATRIX-MULTIPLY-RECURSIVE to multiply nn matrices for which n is not necessarily an exact power of 2. Give a recurrence describing its running time. Argue that it runs in ‚.n3/ time in the worst case.

4.1-2

How quickly can you multiply a kn  n matrix (kn rows and n columns) by an n  kn matrix, where k1, using MATRIX-MULTIPLY-RECURSIVE as a subroutine? Answer the same question for multiplying an n  kn matrix by a kn  n matrix. Which is asymptotically faster, and by how much?

## 4.2 Strassen’s algorithm for matrix multiplication 4.1-3

Suppose that instead of partitioning matrices by index calculation in MATRIXMULTIPLY- RECURSIVE, you copy the appropriate elements of A, B, and C into separate n=2  n=2 submatrices A11, A12, A21, A22; B11, B12, B21, B22; and C11, C12, C21, C22,respectively. Aftertherecursivecalls,youcopytheresultsfrom C11, C12, C21, and C22 back into the appropriate places in C . How does recurrence (4.9) change, and what is its solution?

4.1-4

Writepseudocode fora divide-and-conquer algorithm MATRIX-ADD-RECURSIVE that sums two nn matrices A and B by partitioning each of them into four n=2  n=2 submatrices and then recursively summing corresponding pairs of sub- matrices. Assume that matrix partitioning uses ‚.1/-time index calculations. Write a recurrence for the worst-case running time of MATRIX-ADD-RECURSIVE, and solve your recurrence. What happens if you use ‚.n2/-time copying to implement the partitioning instead of index calculations?

## 4.2 Strassen’s algorithm for matrix multiplication You might ûnd it hard to imagine that any matrix multiplication algorithm could take less than ‚.n3/ time, since the natural deûnition of matrix multiplication requires n3 scalar multiplications. Indeed, many mathematicians presumed that it was not possible to multiply matrices in o.n3/ time until 1969, when V. Strassen

[424] published a remarkable recursive algorithm for multiplying nn matrices. Strassen’s algorithm runs in ‚.nlg7/ time. Since lg7 D 2:8073549 : : :, Strassen’s algorithm runs in O.n2:81/ time, which is asymptotically better than the ‚.n3/MATRIX-MULTIPLY and MATRIX-MULTIPLY-RECURSIVE procedures. The key to Strassen’s method is to use the divide-and-conquer idea from the MATRIX-MULTIPLY-RECURSIVE procedure, but make the recursion tree less bushy. We’ll actually increase the work for each divide and combine step by a constant factor, but the reduction in bushiness will pay off. We won’t reduce the bushiness from the eight-way branching of recurrence (4.9) all the way down to the two-way branching of recurrence (2.3), but we’ll improve it just a little, and that will make a big difference. Instead of performing eight recursive multiplications of n=2  n=2 matrices, Strassen’s algorithm performs only seven. The cost of eliminating one matrix multiplication is several new additions and subtractionsof n=2  n=2 matrices, but still only a constant number. Rather than saying <additions and subtractions= everywhere, we’ll adopt the common terminology of call

ing them both <additions= because subtraction is structurally the same computationas addition, except for a change of sign.

To get an inkling how the number of multiplications might be reduced, as wellas why reducing the number of multiplications might be desirable for matrix calculations, suppose that you have two numbers x and y, and you want to calculate the quantity x2 y2. The straightforward calculation requires two multiplications to square x and y, followed by one subtraction (which you can think of as a <negative addition=). But let’s recall the old algebra trick x2y2 Dx2xy Cxy y2 D

x.x y/ Cy.x y/ D .x Cy/.x y/. Using this formulation of the desiredquantity, you could instead compute the sum xCy and the difference xy and then multiply them, requiring only a single multiplication and two additions. At the cost of an extra addition, only one multiplication is needed to compute an expression that looks as if it requires two. If x and y are scalars, there’s not much difference: both approaches require three scalar operations. If x and y are largematrices, however, the cost of multiplying outweighs the cost of adding, in whichcase the second method outperforms the ûrst, although not asymptotically. Strassen’s strategy for reducing the number of matrix multiplications at the expense of more matrix additions is not at all obvious4perhaps the biggest understatement in this book! As with MATRIX-MULTIPLY-RECURSIVE, Strassen’s algorithm uses the divide-and-conquer method to compute C DCCAB, where A, B, and C are all nn matrices and n is an exact power of 2. Strassen’s algorithm computes the four submatrices C11, C12, C21, and C22 of C from equations (4.5)3(4.8) on page 82 in four steps. We’ll analyze costs as we go along to develop a recurrence T .n/ for the overall running time. Let’s see how it works:

1. If nD1, the matrices each contain a single element. Perform a single scalarmultiplication and a single scalar addition, as in line 3 of MATRIX-MULTIPLYRECURSIVE, taking ‚.1/ time, and return. Otherwise, partition the input matrices A and B and output matrix C into n=2  n=2 submatrices, as in equation (4.2). This step takes ‚.1/ time by index calculation, just as in MATRIXMULTIPLY- RECURSIVE. 2. Create n=2  n=2 matrices S1; S2; : : : ; S10, each of which is the sum or difference of two submatrices from step 1. Create and zero the entries of seven n=2  n=2 matrices P1; P2; : : : ; P7 to hold seven n=2  n=2 matrix products. All 17 matrices can be created, and the Pi initialized, in ‚.n2/ time. 3. Using the submatrices from step 1 and the matrices S1; S2; : : : ; S10 created in step 2, recursively compute each of the seven matrix products P1; P2; : : : ; P7, taking 7T .n=2/ time. 4. Update the four submatrices C11; C12; C21; C22 ofthe result matrix C by adding or subtracting various Pi matrices, which takes ‚.n2/ time.

## 4.2 Strassen’s algorithm for matrix multiplication 87 We’ll see the details of steps 234 in a moment, but we already have enough information to set up a recurrence for the running time of Strassen’s method. As is common, the base case in step 1 takes ‚.1/ time, which we’ll omit when stating the recurrence. When n>1, steps 1, 2, and 4 take a total of ‚.n2/ time, and step 3 requires seven multiplications of n=2  n=2 matrices. Hence, we obtain the following recurrence for the running time of Strassen’s algorithm:

T .n/ D 7T .n=2/ C ‚.n2/ : (4.10)

Compared with MATRIX-MULTIPLY-RECURSIVE, we have traded off one recursive submatrix multiplication for a constant number of submatrix additions. Once you understand recurrences and their solutions, you’ll be able to see whythis trade- off actually leads to alower asymptotic running time. Bythe master method inSection 4.5, recurrence (4.10) has the solution T .n/ D ‚.nlg7/ D O.n2:81/, beating the ‚.n3/-time algorithms.

Now, let’s delve into the details. Step 2 creates the following 10 matrices:

S1 D B12 B22 ; S2 D A11 CA12 ; S3 D A21 CA22 ; S4 D B21 B11 ; S5 D A11 CA22 ; S6 D B11 CB22 ; S7 D A12 A22 ; S8 D B21 CB22 ; S9 D A11 A21 ; S10 D B11 CB12 :

This step adds or subtracts n=2  n=2 matrices 10 times, taking ‚.n2/ time.

Step 3 recursively multiplies n=2  n=2 matrices 7 times to compute the following n=2  n=2 matrices, each of which is the sum or difference of products of A and B submatrices:

P1 D A11 S1 .D A11 B12 A11 B22/; P2 D S2B22 .D A11 B22 CA12 B22/; P3 D S3B11 .D A21 B11 CA22 B11/; P4 D A22 S4 .D A22 B21 A22 B11/; P5 D S5S6 .D A11 B11 CA11 B22 CA22 B11 CA22 B22/; P6 D S7S8 .D A12 B21 CA12 B22 A22 B21 A22 B22/; P7 D S9S10 .D A11 B11 CA11 B12 A21 B11 A21 B12/:

The only multiplications that the algorithm performs are those in the middle column of these equations. The right-hand column just shows what these products equal in terms of the original submatrices created in step 1, but the terms are never explicitly calculated by the algorithm.

Step 4 adds to and subtracts from the four n=2  n=2 submatrices of the product C the various Pi matrices created in step 3. We start with

C11 DC11 CP5CP4P2CP6:

Expanding the calculation on the right-hand side, with the expansion of each Pi on its own line and vertically aligning terms that cancel out, we see that the updateto C11 equals

A11 B11 CA11 B22 CA22 B11 CA22 B22  A22 B11 CA22 B21  A11 B22  A12 B22  A22 B22  A22 B21 CA12 B22 CA12 B21

A11 B11 CA12 B21 ;

which corresponds to equation (4.5). Similarly, setting

C12 DC12 CP1CP2 means that the update to C12 equals A11 B12  A11 B22 CA11 B22 CA12 B22

A11 B12 CA12 B22 ;

corresponding to equation (4.6). Setting

C21 DC21 CP3CP4 means that the update to C21 equals A21 B11 CA22 B11  A22 B11 CA22 B21

A21 B11 CA22 B21 ;

corresponding to equation (4.7). Finally, setting

C22 DC22 CP5CP1P3P7 means that the update to C22 equals

## 4.2 Strassen’s algorithm for matrix multiplication 89 A11 B11 CA11 B22 CA22 B11 CA22 B22  A11 B22 CA11 B12 A22 B11 A21 B11 A11 B11 A11 B12 CA21 B11 CA21 B12

A22 B22 CA21 B12 ;

whichcorresponds toequation (4.8). Altogether, sinceweadd orsubtract n=2n=2 matrices 12 times in step 4, this step indeed takes ‚.n2/ time.

We can see that Strassen’s remarkable algorithm, comprising steps 134, produces the correct matrix product using 7 submatrix multiplications and 18 submatrixadditions. Wecanalsoseethatrecurrence(4.10)characterizes its running time. Since Section 4.5 shows that this recurrence has the solution T .n/ D ‚.nlg7/ D o.n3/, Strassen’s method asymptotically beats the ‚.n3/ MATRIX-MULTIPLY and MATRIX-MULTIPLY-RECURSIVE procedures.

## Exercises

Note: You may wish to read Section 4.5 before attempting some of these exercises.

4.2-1

Use Strassen’s algorithm to compute the matrix product

Î ÏÎ Ï

13 68

:

75 42

Show your work.

4.2-2

Write pseudocode for Strassen’s algorithm.

4.2-3

What is the largest k such that if you can multiply 33 matrices using k multiplications (not assuming commutativity of multiplication), then you can multiply nn matrices in o.nlg7/ time? What is the running time of this algorithm?

4.2-4

V. Pan discovered a way of multiplying 68 68 matrices using 132,464 multiplications, a way of multiplying 70  70 matrices using 143,640 multiplications, and a way of multiplying 72  72 matrices using 155,424 multiplications. Which method yields the best asymptotic running time when used in a divide-and-conquermatrix-multiplication algorithm? How does it compare with Strassen’s algorithm?

4.2-5

Show how to multiply the complex numbers a C bi and c C di using only three multiplications of real numbers. The algorithm should take a, b, c, and d as input and produce the real component ac bd and the imaginary component ad Cbc separately.

4.2-6

Suppose that you have a ‚.n˛/-time algorithm for squaring nn matrices, where ˛2. Show how to use that algorithm to multiply two different nn matrices in ‚.n˛/ time.

## 4.3 The substitution method for solving recurrences Now that you have seen how recurrences characterize the running times of divideand- conquer algorithms, let’s learn how to solve them. We start in this section with the substitution method, which is the most general of the four methods in this chapter. The substitution method comprises two steps:

1. Guess the form of the solution using symbolic constants. 2. Use mathematical induction to show that the solution works, and ûnd the constants. To apply the inductive hypothesis, you substitute the guessed solution for the function on smaller values4hence the name <substitution method.= This method is powerful, but you must guess the form of the answer. Although generating a goodguess might seem difûcult, a little practice can quickly improve your intuition.

You can use the substitution method to establish either an upper or alower bound on a recurrence. It’s usually best not to try to do both at the same time. That is, rather than trying to prove a ‚-bound directly, ûrst prove an O-bound, and then prove an Y-bound. Together, they give you a ‚-bound (Theorem 3.1 on page 56).

As an example of the substitution method, let’s determine an asymptotic upper bound on the recurrence:

T .n/ D 2T .bn=2c/ C ‚.n/ : (4.11)

This recurrence is similar to recurrence (2.3) on page 41 for merge sort, except for the üoor function, which ensures that T .n/ is defined over the integers. Let’s guess that the asymptotic upper bound is the same4T .n/ D O.n lgn/4and use the substitution method to prove it.

We’ll adopt the inductive hypothesis that T .n/ හ cn lgn for all n  n0, where we’ll choose the speciûc constants c>0 and n0 > 0 later, after we see what

## 4.3 The substitution method for solving recurrences 91 constraints they need to obey. If we can establish this inductive hypothesis, we can

concludethat lg Itwouldbedangeroustouse lg T.n/ DO.n n/ T.n/ DO.n n/ . astheinductivehypothesisbecausetheconstantsmatter,aswe’llseeinamoment Assumebyinductionthatthisboundholdsforallnumbersatleastasbigas n0 andlessthan Inparticular,therefore,if ,itholdsfor ,yielding 2n n=2bnnc. 0 lg Substitutinginto (4.11)4hence the T. n=2 /හn=2 n=2 /bbb recurrence cccc .. 0

in our discussion of pitfalls.

name<substitution= method4yieldslg T.n/ හ2.c n=2 n=2 // C‚.n/ bbcc. lg හ2.c.n=2/ .n=2// C‚.n/ lg lg D2C‚.n/ cn ncn wherethelaststepholdsifweconstraintheconstants and tobesufficiently nc0 0

D cn lg.n=2/ C ‚.n/

D cn lgn  cn C ‚.n/

හ cn lgn;

large that for n  2n0, the quantity cn dominates the anonymous function hidden by the ‚.n/ term.

We’ve shown that the inductive hypothesis holds for the inductive case, but we also need to prove that the inductive hypothesis holds for the base cases of the induction, that is, that T .n/ හ cn lgn when n0 හn< 2n0. As long as n0 > 1 (a new constraint on n0), we have lgn>0, which implies that n lgn>0. So let’s pick n0 D2. Since the base case of recurrence (4.11) is not stated explicitly, by our convention, T .n/ is algorithmic, which means that T .2/ and T .3/ are constant (as they should be if they describe the worst-case running time of any real program on inputs of size 2 or 3). Picking cD maxfT .2/; T .3/g yields T.2/ හc < .2 lg2/c and T.3/ හc <.3 lg3/c, establishing the inductive hypothesis for the base cases.

Thus, we have T .n/ හ cn lgn for all n2, which implies that the solution to recurrence (4.11) is T .n/ D O.n lgn/.

In the algorithms literature, people rarely carry out their substitution proofs to this level of detail, especially in their treatment of base cases. The reason is that for most algorithmic divide-and-conquer recurrences, the base cases are all handled in pretty much the same way. You ground the induction on a range of values from a

0 > n0 such that for n  n0, convenient positive constant n0 up to some constant n

the recurrence always bottoms out in a constant-sized base case between n0 and n0.

D 2n0.) Then, it’s usually apparent, without spelling outthe details, that with a suitably large choice of the leading constant (such as c for this example), the inductive hypothesis can be made to hold for all the values in the

0.

(This example used n

range from n0 to n

Making a good guess

Unfortunately, there is no general way to correctly guess the tightest asymptotic solution to an arbitrary recurrence. Making a good guess takes experience and, occasionally, creativity. Fortunately, learning some recurrence-solving heuristics, as wellasplaying around withrecurrences togainexperience, canhelpyoubecome

a good guesser. You can also use recursion trees, which we’ll see in Section 4.4, to

help generate good guesses.

If a recurrence is similar to one you’ve seen before, then guessing a similar solution is reasonable. As an example, consider the recurrence

T.n/ D 2T.n=2 C17/ C‚.n/ ;

defined on the reals. This recurrence looks somewhat like the merge-sort recurrence (2.3), but it’s more complicated because of the added <17= in the argument to T on the right-hand side. Intuitively, however, this additional term shouldn’t substantially affect the solution to the recurrence. When n is large, the relative difference between n=2 and n=2 C 17 is not that large: both cut n nearly in half. Consequently, itmakes sense toguess that T .n/ D O.n lgn/, whichyou can verify

is correct using the substitution method (see Exercise 4.3-1).

Another way tomake a good guess isto determine loose upper and lowerbounds on the recurrence and then reduce your range of uncertainty. For example, you might start with a lower bound of T .n/ D Y.n/ for recurrence (4.11), since the recurrence includes the term ‚.n/, and you can prove an initial upper bound of T .n/ D O.n2/. Then split your time between trying to lower the upper bound andtrying to raise the lower bound until you converge on the correct, asymptotically tight solution, which in this case is T .n/ D ‚.n lgn/.

A trick of the trade: subtracting a low-order term

Sometimes, you might correctly guess a tight asymptotic bound on the solution of a recurrence, but somehow the math fails to work out in the induction proof. The problem frequently turns out to be that the inductive assumption is not strongenough. The trick to resolving this problem is to revise your guess by subtracting a lower-order term when you hit such a snag. The math then often goes through.

Consider the recurrence

T .n/ D 2T .n=2/ C ‚.1/ (4.12) defined on the reals. Let’s guess that the solution is T .n/ D O.n/ and try to show that T .n/ හ cn for n n0, where we choose the constants c;n0 >0 suitably. Substituting our guess into the recurrence, we obtain

T .n/ හ 2.c.n=2// C ‚.1/ D cn C‚.1/;

## 4.3 The substitution method for solving recurrences 93 which, unfortunately, does not imply that T .n/ හ cn for any choice of c. Wemight be tempted to try a larger guess, say T .n/ D O.n2/. Although this larger guess works, it provides only a loose upper bound. It turns out that our original guess of T .n/ D O.n/ is correct and tight. In order to show that it is correct, however, wemust strengthen our inductive hypothesis.

Intuitively, our guess is nearly right: we are off only by ‚.1/, a lower-order term. Nevertheless, mathematical induction requires us to prove the exact form of the inductive hypothesis. Let’s try our trick of subtracting a lower-order term from our previous guess: T.n/ හ cn d, where d 0 is a constant. We now have

T.n/ හ 2.c.n=2/  d/ C ‚.1/

D cn 2d C‚.1/

හ cn d .d ‚.1//

හ cn d

as long as we choose d to be larger than the anonymous upper-bound constant hidden by the ‚-notation. Subtracting a lower-order term works! Of course, we must not forget to handle the base case, which is to choose the constant c large enough that cn  d dominates the implicit base cases.

You might ûnd the idea of subtracting a lower-order term to be counterintuitive. After all, if the math doesn’t work out, shouldn’t you increase your guess? Not necessarily! When the recurrence contains more than one recursive invocation (recurrence (4.12) contains two), if you add a lower-order term to the guess, then you end up adding it once for each of the recursive invocations. Doing so takes you even further away from the inductive hypothesis. On the other hand, if you subtract a lower-order term from the guess, then you get to subtract it once for each of the recursive invocations. In the above example, we subtracted the constant d twice because the coefûcient of T .n=2/ is 2. We ended up with the inequality T.n/ හcn d .d ‚.1//, and we readily found a suitable value for d .

Avoiding pitfalls

Avoid using asymptotic notation in the inductive hypothesis for the substitution

method because it’s error prone. For example, for recurrence (4.11), we can falsely

<prove= that T .n/ D O.n/ if we unwisely adopt T .n/ D O.n/ as our inductive hypothesis:

T .n/ හ 2  O.bn=2c/ C ‚.n/

D 2  O.n/ C ‚.n/

D O.n/ : Ń wrong!

The problem with this reasoning is that the constant hidden by the O-notation changes. We can expose the fallacy by repeating the <proof= using an explicit constant. For the inductive hypothesis, assume that T .n/ හ cn for all n  n0, where c;n0 > 0 are constants. Repeating the ûrst two steps in the inequality chain yields

T .n/ හ 2.c bn=2c/ C ‚.n/ හ cn C‚.n/: Now,indeed cnC‚.n/ D O.n/, buttheconstant hidden by the O-notation mustbe larger than c because theanonymous function hidden bythe ‚.n/ is asymptotically positive. We cannot take the third step to conclude that cn C‚.n/ හ cn, thus exposing the fallacy. When using the substitution method, or more generally mathematical induction, you must be careful that the constants hidden by any asymptotic notation are the same constants throughout the proof. Consequently, it’s best to avoid asymptoticnotation in your inductive hypothesis and to name constants explicitly.

Here’s another fallacious use of the substitution method to show that the solution to recurrence (4.11) is T .n/ D O.n/. We guess T .n/ හ cn and then argue T .n/ හ 2.c bn=2c/ C ‚.n/

හ cn C ‚.n/

D O.n/ ; Ń wrong! since c is a positive constant. The mistake stems from the difference between our goal4to prove that T .n/ D O.n/4and our inductive hypothesis4to prove that T .n/ හ cn. When using the substitution method, or in any inductive proof, you must prove the exact statement of the inductive hypothesis. In this case, we must explicitly prove that T .n/ හ cn to show that T .n/ D O.n/.

## Exercises

4.3-1

Use the substitution method to show that each of the following recurrences defined on the reals has the asymptotic solution speciûed:

a. T.n/ D T.n 1/ Cn has solution T .n/ D O.n2/. b. T .n/ D T .n=2/ C ‚.1/ has solution T .n/ D O.lgn/. c. T.n/ D 2T.n=2/ Cn has solution T .n/ D ‚.n lgn/. d. T.n/ D 2T.n=2 C17/ Cn has solution T .n/ D O.n lgn/. e. T .n/ D 2T .n=3/ C ‚.n/ has solution T .n/ D ‚.n/. f. T .n/ D 4T .n=2/ C ‚.n/ has solution T .n/ D ‚.n2/.

## 4.4 The recursion-tree method for solving recurrences 4.3-2

Thesolution to the recurrence T.n/ D 4T.n=2/Cn turns out to be T .n/ D ‚.n2/. Show that a substitution proof with the assumption T .n/ හ cn2 fails. Then show how to subtract a lower-order term to make a substitution proof work.

4.3-3

The recurrence T.n/ D 2T.n1/C1 has the solution T .n/ D O.2n/. Show that a substitution proof fails with the assumption T .n/ හ c2n, where c>0 is constant. Then show how to subtract a lower-order term to make a substitution proof work.

## 4.4 The recursion-tree method for solving recurrences Although you can use the substitution method to prove that a solution to a recurrence is correct, you might have trouble coming up with a good guess. Drawing

out a recursion tree, as we did in our analysis of the merge-sort recurrence in Section 2.3.2, can help. In a recursion tree, each node represents the cost of a singlesubproblem somewhere in the set of recursive function invocations. You typically sum thecosts within each levelofthetree to obtain theper-level costs, andthen you sum all the per-level costs to determine the total cost of all levels of the recursion. Sometimes, however, adding up the total cost takes more creativity.

A recursion tree is best used to generate intuition for a good guess, which you can then verify by the substitution method. If you are meticulous when drawing outa recursion tree and summing the costs, however, you can use a recursion tree as adirect proof of a solution to a recurrence. But if you use it only to generate a goodguess, you can often tolerate a small amount of <sloppiness,= which can simplify the math. When you verify your guess with the substitution method later on, yourmath should be precise. This section demonstrates how you can use recursion treesto solve recurrences, generate good guesses, and gain intuition for recurrences.

An illustrative example

Let’sseehowarecursion tree can provide agood guess for anupper-bound solution

to the recurrence

T .n/ D 3T .n=4/ C ‚.n2/ : (4.13)

Figure 4.1 shows how to derive the recursion tree for T .n/ D 3T .n=4/ C cn2, where the constant c>0 is the upper-bound constant in the ‚.n2/ term. Part (a) of the ûgure shows T .n/, which part (b) expands into an equivalent tree representing the recurrence. The cn2 term at the root represents the cost at the top levelof recursion, and the three subtrees of the root represent the costs incurred by the

T.n/ cn2 cn2

T n4ÍT n4ÍT n4ÍT n16ÍT n16ÍT n16ÍT n16ÍT n16ÍT n16ÍT n16ÍT n16ÍT n16Íc n4Í2c n4Í2c n4Í2 (a) (b) (c) cn2 cn2

… cÍ2Í2nnn4c44  c Í2cÍ2Í2nnnnnnnnn161616161616161616c  c Í2c Í2c Í2c Í2c Í2c Í2c Í2 32

cn

log4n

Î Ï2

cn

‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ … ‚.1/ ‚.1/ ‚.1/ ‚.nlog4 3/

3log4nDnlog43

Total: O.n2/

(d)

Figure 4.1 Constructing a recursion tree for the recurrence T .n/ D 3T .n=4/ C cn2. Part (a) shows T .n/, which progressively expands in (b)–(d) to form the recursion tree. The fully expanded tree in (d) has height log4n.

## 4.4 The recursion-tree method for solving recurrences 97 subproblems of size n=4. Part (c) shows this process carried one step further by expanding each node with cost T .n=4/ from part (b). The cost for each of the three children of the root is c.n=4/2. We continue expanding each node in the tree bybreaking it into its constituent parts as determined by the recurrence.

Because subproblem sizes decrease by a factor of 4 every time we go down onelevel, the recursion must eventually bottom out in a base case where n < n0. By convention, the base case is T .n/ D ‚.1/ for n < n0, where n0 > 0 is any threshold constant sufficiently large that the recurrence is well defined. For the purpose of intuition, however, let’s simplify the math a little. Let’s assume that n is an exact power of 4 and that the base case is T .1/ D ‚.1/. As it turns out, these assumptions don’t affect the asymptotic solution.

What’s the height of the recursion tree? The subproblem size for a node at depth i is n=4i . As we descend the tree from the root, the subproblem size hits nD1 when n=4i D1 or, equivalently, when iD log4n. Thus, the tree has internal nodes at depths 0;1;2;::: ; log4n1 and leaves at depth log4n.

Part (d) of Figure 4.1 shows the cost at each level of the tree. Each level has three times as many nodes as the level above, and so the number of nodes at depth i is 3i . Because subproblem sizes reduce by a factor of 4 for each level further from the root, each internal node at depth i D0;1;2;:::; log4n1 has a cost of c.n=4i/2. Multiplying, we see that the total cost of all nodes at a given depth i is 3ic.n=4i/2 D .3=16/icn2. The bottom level, at depth log4n, contains 3log4n Dnlog43 leaves (using equation (3.21) on page 66). Each leaf contributes ‚.1/, leading to a total leaf cost of ‚.nlog4 3/.

Now we add up the costs over all levels to determine the cost for the entire tree:

ÎÏ2 ÎÏlog4n T.n/ D cn2C 3 cn2C 3 cn2CC 3 cn2C‚.nlog4 3/

16 16 16

log4nÎ 3 Ïi

D X cn2C‚.nlog4 3/

iD0

1Î Ïi

< X cn2C‚.nlog4 3/

iD0

D 1 cn2C‚.nlog4 3/ (by equation (A.7) on page 1142)

1  .3=16/

D 16 cn2 C ‚.nlog4 3/

13 D O.n2/ (‚.nlog4 3/ D O.n0:8/ D O.n2/).

We’vederived theguessof T .n/ D O.n2/ fortheoriginalrecurrence. Inthisexample, the coefûcients of cn2 form a decreasing geometric series. By equation (A.7), the sum of these coefûcients is bounded from above by the constant 16=13. Since

the root’s contribution to the total cost is cn2, the cost of the root dominates the total cost of the tree.

In fact, if O.n2/ is indeed an upper bound for the recurrence (as we’ll verify in

a moment), then it must be a tight bound. Why? The ûrst recursive call contributes

a cost of ‚.n2/, and so Y.n2/ must be a lower bound for the recurrence.

Let’s now use the substitution method to verify that our guess is correct, namely, that T .n/ D O.n2/ isanupper bound for therecurrence T .n/ D 3T .n=4/C‚.n2/. We want to show that T.n/ හ dn2 for some constant d >0. Using the same constant c>0 as before, we have

T .n/ හ 3T .n=4/ C cn2 හ 3d.n=4/2 C cn2 3

D dn2 C cn2

16 හ dn2 ;

where the last step holds if we choose d  .16=13/c.

For the base case of the induction, let n0 >0 be a sufficiently large threshold constant that the recurrence is well defined when T .n/ D ‚.1/ for n < n0. We can pick d large enough that d dominates the constant hidden by the ‚, in which case dn2d T.n/ for 1 හ n < n0, completing the proof of the base case.

The substitution proof we just saw involves two named constants, c and d . We named c and used it tostand for the upper-bound constant hidden and guaranteed to exist by the ‚-notation. We cannot pick c arbitrarily4it’s given to us4although, for any such c, any constant c0 c also sufûces. We also named d , but we were free to choose any value for it that ût our needs. In this example, the value of d happened to depend on the value of c, which is ûne, since d is constant if c is constant.

An irregular example

Let’s ûnd an asymptotic upper bound for another, more irregular, example. Figure 4.2 shows the recursion tree for the recurrence

T .n/ D T .n=3/ C T .2n=3/ C ‚.n/ : (4.14)

This recursion tree is unbalanced, with different root-to-leaf paths having different lengths. Going left at any node produces a subproblem of one-third the size, and going right produces asubproblem oftwo-thirds the size. Let n0 > 0 betheimplicit threshold constant such that T .n/ D ‚.1/ for 0 < n < n0, and let c represent the upper-bound constant hidden by the ‚.n/ term for n  n0. There are actually two n0 constants here4one for the threshold in the recurrence, and the other for the threshold in the ‚-notation, so we’ll let n0 be the larger of the two constants.

## 4.4 The recursion-tree method for solving recurrences 99 cn

cn

cn

Ú

log3=2.n=n0/ C 1

‚.1/‚.1/ ‚.1/ ‚.1/

‚.1/

‚.1/

‚.1/

‚.1/

‚.1/ ‚.1/

‚.1/

Figure 4.2 A recursion tree for the recurrence T .n/ D T .n=3/ C T .2n=3/ C cn.

The height of the tree runs down the right edge of the tree, corresponding to subproblems ofsizes n; .2=3/n; .4=9/n; : : : ; ‚.1/ withcostsbounded by cn; c.2n=3/; c.4n=9/; : : : ; ‚.1/, respectively. We hit the rightmost leaf when .2=3/hn < n0 හ .2=3/h1n, which happens when hDblog3=2.n=n0/c C 1 since, applying the üoor bounds in equation (3.2) on page 64 with xD log3=2.n=n0/, we have .2=3/hn D .2=3/bxcC1n < .2=3/xn D .n0=n/n D n0 and .2=3/h1n D .2=3/bxcn > .2=3/xn D .n0=n/n D n0. Thus, the height of the tree is h D ‚.lgn/.

We’re now in a position to understand the upper bound. Let’s postpone dealing with the leaves for a moment. Summing the costs of internal nodes across each level, we have at most cn per level times the ‚.lgn/ tree height for a total cost of

O.n lgn/ for all internal nodes. It remains to deal with the leaves of the recursion tree, which represent base cases, each costing ‚.1/. How many leaves are there? It’s tempting to upper- bound their number by the number of leaves in a complete binary tree of height

hDblog3=2.n=n0/c C 1, since the recursion tree is contained within such a com

plete binary tree. But this approach turns out to give us a poor bound. The complete binary tree has 1 node at the root, 2 nodes at depth 1, and generally 2k nodes at depth k. Since the height is hDblog3=2 nc C 1, there are

cnc n3ÍcÎ2n3Ïc n9ÍcÎ2n9ÏcÎ2n9ÏcÎ4n9Ï …

…

Total:O.nlgn/ ‚.n/

2h D2blog3=2 ncC1 හ 2nlog3=2 2 leaves in the complete binary tree, which is an upper bound on the number of leaves in the recursion tree. Because the cost of each leaf is ‚.1/, this analysis says that the total cost of all leaves in the recursion tree is O.nlog3=2 2/ D O.n1:71/, which is an asymptotically greater bound than the

O.n lgn/ cost of all internal nodes. In fact, as we’re about to see, this bound is not tight. The cost of all leaves in the recursion tree is O.n/4asymptotically less than O.n lgn/. In other words, the cost of the internal nodes dominates the cost ofthe leaves, not vice versa. Rather than analyzing the leaves, we could quit right now and prove by substitution that T .n/ D ‚.n lgn/. This approach works (see Exercise 4.4-3), but it’s instructive to understand how many leaves this recursion tree has. You may see recurrences for which the cost of leaves dominates the cost of internal nodes, andthen you’ll be in better shape if you’ve had some experience analyzing the number of leaves.

To ûgure out how many leaves there really are, let’s write a recurrence L.n/ for the number of leaves in the recursion tree for T .n/. Since all the leaves in T .n/ belong either to the left subtree or the right subtree of the root, we have

(

1 if n < n0 ;

L.n/ D (4.15)

L.n=3/ C L.2n=3/ if n  n0 :

This recurrence is similar to recurrence (4.14), but it’s missing the ‚.n/ term, and it contains an explicit base case. Because this recurrence omits the ‚.n/ term, it is much easier to solve. Let’s apply the substitution method to show that it has solution L.n/ D O.n/. Using the inductive hypothesis L.n/ හ dn for some constant d >0, and assuming that the inductive hypothesis holds for all values less than n, we have

L.n/ D L.n=3/ C L.2n=3/

හ dn=3 C 2.dn/=3

හ dn;

which holds for any d >0. We can now choose d large enough to handle the base case L.n/ D 1 for 0 < n < n0, for which d D1 sufûces, thereby completing the substitution method for the upper bound on leaves. (Exercise 4.4-2 asks you to prove that L.n/ D ‚.n/.)

Returning to recurrence (4.14) for T .n/, it now becomes apparent that the total cost of leaves over all levels must be L.n/  ‚.1/ D ‚.n/. Since we have derived the bound of O.n lgn/ on the cost of the internal nodes, it follows that the solution to recurrence (4.14) is T .n/ D O.n lgn/ C‚.n/ D O.n lgn/. (Exercise 4.4-3 asks you to prove that T .n/ D ‚.n lgn/.)

It’s wise to verify any bound obtained with a recursion tree by using the substitution method, especially if you’ve made simplifying assumptions. But another

## 4.5 The master method for solving recurrences strategy altogether is to use more-powerful mathematics, typically in the form ofthe master method in the next section (which unfortunately doesn’t apply to recurrence (4.14)) or the Akra-Bazzi method (which does, but requires calculus). Even ifyou use apowerful method, a recursion tree can improveyour intuition for what’s going on beneath the heavy math.

## Exercises

4.4-1

For each of the following recurrences, sketch its recursion tree, and guess a good asymptotic upper bound on its solution. Then use the substitution method to verify your answer.

a. T.n/ D T.n=2/ Cn3. b. T.n/ D 4T.n=3/ Cn. c. T.n/ D 4T.n=2/ Cn. d. T.n/ D 3T.n 1/ C1. 4.4-2

Use the substitution method to prove that recurrence (4.15) has the asymptotic lower bound L.n/ D Y.n/. Conclude that L.n/ D ‚.n/.

4.4-3

Usethesubstitution methodtoprovethat recurrence (4.14) hasthesolution T .n/ D

Y.n lgn/. Conclude that T .n/ D ‚.n lgn/. 4.4-4

Use a recursion tree to justify a good guess for the solution to the recurrence T.n/ D T.˛n/CT..1˛/n/C‚.n/,where ˛ isaconstant inthe range 0<˛<1.

## 4.5 The master method for solving recurrences The master method provides a <cookbook= method for solving algorithmic recurrences of the form

T.n/ D aT.n=b/ Cf.n/; (4.16) where a>0 and b>1 are constants. We call f .n/ a driving function, and we call a recurrence of this general form a master recurrence. To use the master method, you need to memorize three cases, but then you’ll be able to solve many master recurrences quite easily.

A master recurrence describes the running time of a divide-and-conquer algo

rithm that divides a problem of size n into a subproblems, each of size n=b<n . The algorithm solves the a subproblems recursively, each in T .n=b/ time. The driving function f .n/ encompasses the cost of dividing the problem before the recursion, as well as the cost of combining the results of the recursive solutions to subproblems. For example, the recurrence arising from Strassen’s algorithm is a master recurrence with aD7, bD2, and driving function f .n/ D ‚.n2/.

As we have mentioned, in solving a recurrence that describes the running timeof an algorithm, one technicality that we’d often prefer to ignore is the requirement that the input size n be an integer. For example, we saw that the running time of merge sort can be described by recurrence (2.3), T .n/ D 2T .n=2/ C ‚.n/, on page 41. But if n is an odd number, we really don’t have two problems of

exactly half the size. Rather, to ensure that the problem sizes are integers, weround one subproblem down to size bn=2c and the other up to size dn=2e, so the true recurrence is T .n/ D T .dn=2e C T .bn=2c/ C ‚.n/. But this üoors-and-ceilingsrecurrence is longer to write and messier to deal with than recurrence (2.3), which is defined on the reals. We’d rather not worry about üoors and ceilings, if we don’t

have to, especially since the two recurrences have the same ‚.n lgn/ solution.

The master method allows you to state a master recurrence without üoors and ceilings and implicitly infer them. No matter how the arguments are rounded upor down to the nearest integer, the asymptotic bounds that it provides remain the same. Moreover, as we’ll see in Section 4.6, if you deûne your master recurrence on the reals, without implicit üoors and ceilings, the asymptotic bounds still don’tchange. Thusyoucanignoreüoorsandceilingsformasterrecurrences. Section4.7 gives sufûcient conditions for ignoring üoors and ceilings in more general divideand- conquer recurrences.

The master theorem

The master method depends upon the following theorem.

Theorem 4.1 (Master theorem)

Let a>0 and b>1 be constants, and let f .n/ be a driving function that is defined and nonnegative on all sufficiently large reals. Deûne the recurrence T .n/ on n2N by

T.n/ D aT.n=b/ Cf.n/; (4.17)

where aT .n=b/ actually means a0T .bn=bc/ C a00T .dn=be/ for some constants a0 0 and a00 0 satisfying a Da0Ca00. Then the asymptotic behavior of T .n/ can be characterized as follows:

## 4.5 The master method for solving recurrences 103 1. If there exists a constant >0 such that f .n/ D O.nlogb a/, then T .n/ D ‚.nlogb a/. 2. If there exists a constant k0 such that f .n/ D ‚.nlogba lgk n/, then T .n/ D logba lgkC1 n/. ‚.n

3. If there exists a constant >0 such that f .n/ D Y.nlogb aC/, and if f .n/ additionally satisfies the regularity condition af .n=b/ හ cf .n/ for some constant c<1 and all sufficiently large n, then T .n/ D ‚.f .n//. Before applying the master theorem to some examples, let’s spend a few mo

logba

ments to understand broadly what it says. The function n is called the watershed function. In each of the three cases, we compare the driving function f .n/ to

logba

the watershed function n . Intuitively, if the watershed function grows asymptotically faster than the driving function, then case 1 applies. Case 2 applies if the two functions grow at nearly the same asymptotic rate. Case 3 is the <opposite= of case 1, where the driving function grows asymptotically faster than the watershed function. But the technical details matter.

In case 1, not only must the watershed function grow asymptotically faster than the driving function, it must grow polynomially faster. That is, the watershed function nlogba must be asymptotically larger than the driving function f .n/ by at least a factor of ‚.n/ for some constant >0. The master theorem then says that the solution is T .n/ D ‚.nlogb a/. In this case, if we look at the recursion tree for therecurrence, the cost per level grows at least geometrically from root to leaves, andthe total cost of leaves dominates the total cost of the internal nodes.

In case 2, the watershed and driving functions grow at nearly the same asymptotic rate. But more speciûcally, the driving function grows faster than the watershed function by a factor of ‚.lgk n/, where k0. The master theorem says that we tack on an extra lg n factor to f .n/, yielding the solution T .n/ D ‚.nlogba lgkC1 n/. In this case, each level of the recursion tree costs approximately the same4‚.nlogba lgk n/4and there are ‚.lgn/ levels. In practice, the most common situation for case 2 occurs when kD0, in which case the watershed and driving functions have the same asymptotic growth, and the solution is T .n/ D ‚.nlogba lgn/.

Case 3 mirrors case 1. Not only must the driving function grow asymptotically faster than the watershed function, it must grow polynomially faster. That is, the driving function f .n/ must be asymptotically larger than the watershed function nlogba by at least a factor of ‚.n/ for some constant >0. Moreover, the driving function must satisfy the regularity condition that af .n=b/ හ cf .n/. This condition is satisûed by most of the polynomially bounded functions that you’re likelyto encounter when applying case 3. The regularity condition might not be satisûed

if the driving function grows slowly in local areas, yet relatively quickly overall.

(Exercise 4.5-5 gives an example of such a function.) For case 3, the master theo

rem says that the solution is T .n/ D ‚.f .n//. If we look at the recursion tree, thecost per level drops at least geometrically from the root to the leaves, and the rootcost dominates the cost of all other nodes.

It’s worth looking again at the requirement that there be polynomial separation between the watershed function and the driving function for either case 1 or case 3 to apply. The separation doesn’t need to be much, but it must be there, and it must grow polynomially. For example, for the recurrence T .n/ D 4T .n=2/ C n1:99 (admittedly not a recurrence you’re likely to see when analyzing an algorithm), the watershed function is nlogba Dn2. Hence the driving function f .n/ D n1:99 is polynomially smaller by a factor of n0:01. Thus case 1 applies with � D 0:01.

Using the master method

Touse the master method, you determine which case (if any) of the master theoremapplies and write down the answer.

As a ûrst example, consider the recurrence T.n/ D 9T.n=3/ C n. For this recurrence, wehave aD9 and bD3, whichimpliesthat nlogbaDnlog3 9 D ‚.n2). Since f.n/ D n D O.n2/ for any constant හ1, we can apply case 1 of the master theorem to conclude that the solution is T .n/ D ‚.n2/.

Now consider the recurrence T.n/ D T.2n=3/ C 1, which has aD1 and

logba log3=2 1 Dn0 D1.

b D 3=2, which means that the watershed function is n Dn Case 2 applies since f.n/ D 1D‚.nlogba lg0 n/ D ‚.1/. The solution to the recurrence is T .n/ D ‚.lgn/.

For the recurrence T.n/ D 3T.n=4/ Cn lgn, we have aD3 and bD4, which

logba log43

means that n D n D O.n0:793/. Since f.n/ D n lgn D Y.nlog4 3C/, where � canbeaslargeas approximately 0:2, case 3applies aslongasthe regularity condition holds for f .n/. It does, because for sufficiently large n, we have that af .n=b/ D 3.n=4/ lg.n=4/ හ .3=4/n lg n D cf .n/ for c D 3=4. By case 3, the solution to the recurrence is T .n/ D ‚.n lgn/.

Next, let’s look at the recurrence T.n/ D 2T.n=2/ C n lgn, where we have

aD2, bD2, and nlogba Dnlog22 Dn. Case 2 applies since f.n/ D n lgnD

‚.nlogba lg1 n/. We conclude that the solution is T .n/ D ‚.n lg2 n/.

We can use the master method to solve the recurrences we saw in Sections 2.3.2, 4.1, and 4.2.

Recurrence (2.3), T .n/ D 2T .n=2/ C ‚.n/, on page 41, characterizes the running time of merge sort. Since aD2 and bD2, the watershed function is nlogba Dnlog22 Dn. Case 2 applies because f .n/ D ‚.n/, and the solution is T .n/ D ‚.n lgn/.

## 4.5 The master method for solving recurrences 105 Recurrence (4.9), T .n/ D 8T .n=2/ C ‚.1/, on page 84, describes the runningtime of the simple recursive algorithm for matrix multiplication. We have aD8

logba log28

and bD2, which means that the watershed function is n Dn Dn3. Since n3 is polynomially larger than the driving function f .n/ D ‚.1/4indeed, we have f.n/ D O.n3/ for any positive <34case 1 applies. We conclude that T .n/ D ‚.n3/.

Finally, recurrence (4.10), T .n/ D 7T .n=2/ C ‚.n2/, on page 87, arose from the analysis of Strassen’s algorithm for matrix multiplication. For this recurrence,

logba lg7

we have aD7 and bD2, and the watershed function is n Dn . Observing that lg7 D 2:807355 : : :, we can let � D 0:8 and bound the driving function f .n/ D ‚.n2/ D O.nlg7/. Case 1 applies with solution T .n/ D ‚.nlg7/.

When the master method doesn’t apply

There are situations where you can’t use the master theorem. For example, it can be that the watershed function and the driving function cannot be asymptotically

logba

compared. We might have that f.n/  n for an infinite number of values

logba

of n but also that f.n/  n for an infinite number of different values of n. As a practical matter, however, most of the driving functions that arise in the studyof algorithms can be meaningfully compared with the watershed function. If you

encounter a master recurrence for which that’s not the case, you’ll have to resort to

substitution or other methods.

Even when the relative growths of the driving and watershed functions can be compared, the master theorem does not cover all the possibilities. There is a gap between cases 1 and 2 when f .n/ D o.nlogb a/, yet the watershed function does not grow polynomially faster than the driving function. Similarly, there is a gap between cases 2 and 3 when f .n/ D !.nlogb a/ and the driving function grows more than polylogarithmically faster than the watershed function, but it does not grow polynomially faster. If the driving function falls into one of these gaps, or ifthe regularity condition in case 3 fails to hold, you’ll need to use something other than the master method to solve the recurrence.

As an example of a driving function falling into a gap, consider the recurrence T .n/ D 2T .n=2/ C n= lgn. Since aD2 and bD2, the watershed function

logba log22

is n Dn Dn1Dn. The driving function is n= lgn D o.n/, which means that it grows asymptotically more slowly than the watershed function n. But n= lgn grows only logarithmically slower than n, not polynomially slower. More precisely, equation (3.24) on page 67 says that lg n D o.n/ for any constant

>0, which means that 1= lgn D !.n/ and n= lgn D !.n1/ D !.nlogb a/. Thus no constant >0 exists such that n= lgn D O.nlogb a/, which is requiredlogba lgk n/,

for case 1 to apply. Case 2 fails to apply as well, since n= lgn D ‚.n where k D1, but k must be nonnegative for case 2 to apply.

To solve this kind of recurrence, you must use another method, such as the substitution method (Section 4.3) or the Akra-Bazzi method (Section 4.7). (Exercise 4.6-3 asks you to show that the answer is ‚.n lglgn/.) Although the master theorem doesn’t handle this particular recurrence, it does handle the overwhelming majority of recurrences that tend to arise in practice.

## Exercises

4.5-1

Use the master method to give tight asymptotic bounds for the following recurrences.

a. T.n/ D 2T.n=4/ C1. p b. T.n/ D 2T.n=4/ C n. p c. T.n/ D 2T.n=4/ C n lg2n. d. T.n/ D 2T.n=4/ Cn. e. T .n/ D 2T .n=4/ C n2. 4.5-2

Professor Caesar wants to develop a matrix-multiplication algorithm that is asymptotically faster than Strassen’s algorithm. His algorithm will use the divide-and

conquer method, dividing each matrix into n=4  n=4 submatrices, and the divide and combine steps together will take ‚.n2/ time. Suppose that the professor’s algorithm creates a recursive subproblems of size n=4. What is the largest integer value of a for which his algorithm could possibly run asymptotically faster than

Strassen’s?

4.5-3

Use the master method to show that the solution to the binary-search recurrence T .n/ D T .n=2/ C ‚.1/ is T .n/ D ‚.lgn/. (See Exercise 2.3-6 for a description of binary search.)

4.5-4

Consider the function f .n/ D lgn. Argue that although f .n=2/<f .n/ , the regularity condition af .n=b/ හ cf .n/ with aD1 and bD2 does not hold for any constant c<1. Argue further that for any � >0, the condition in case 3 that f .n/ D Y.nlogb aC/ does not hold.

## 4.6 Proof of the continuous master theorem 4.5-5

Show that for suitable constants a, b, and , the function f .n/ D 2dlgne satisfies all the conditions in case 3 of the master theorem except the regularity condition.

## 4.6 Proof of the continuous master theorem

Proving the master theorem (Theorem 4.1) in its full generality, especially dealing with the knotty technical issue of üoors and ceilings, is beyond the scope of this book. This section, however, states and proves a variant of the master theorem, called the continuous master theorem1 in which the master recurrence (4.17) is defined over sufficiently large positive real numbers. The proof of this version, uncomplicated by üoors and ceilings, contains the main ideas needed to understand how master recurrences behave. Section 4.7 discusses üoors and ceilings in divideand- conquer recurrences at greater length, presenting sufûcient conditions for them

not to affect the asymptotic solutions.

Of course, since you need not understand the proof of the master theorem in order to apply the master method, you may choose to skip this section. But if you wish to study more-advanced algorithms beyond the scope of this textbook, you may appreciate a better understanding of the underlying mathematics, which the proof of the continuous master theorem provides.

Although we usually assume that recurrences are algorithmic and don’t requirean explicit statement of a base case, we must be much more careful for proofs thatjustify thepractice. Thelemmas andtheorem inthissection explicitly statethebasecases, because the inductive proofs require mathematical grounding. It is common in the world of mathematics to be extraordinarily careful proving theorems that justify acting more casually in practice.

The proof of the continuous master theorem involves two lemmas. Lemma 4.2 uses a slightly simpliûed master recurrence with a threshold constant of n0 D 1, rather thanthemore general n0 >0 threshold constant implied by the unstated base case. The lemma employs a recursion tree to reduce the solution of the simpliûed master recurrence to that of evaluating a summation. Lemma 4.3 then provides asymptotic bounds for the summation, mirroring the three cases of the master theorem. Finally, the continuous master theorem itself (Theorem 4.4) gives asymptotic bounds for master recurrences, while generalizing to an arbitrary threshold constant n0 >0 as implied by the unstated base case.

1 Thisterminology does not mean that either T .n/ or f .n/ need be continuous, only that the domain of T .n/ is the real numbers, as opposed to integers.

Some of the proofs use the properties described in Problem 3-5 on pages 72373 to combine and simplify complicated asymptotic expressions. Although Problem 3-5 addresses only ‚-notation, the properties enumerated there can be extended to O-notation and Y-notation as well.

Here’s the ûrst lemma.

Lemma 4.2

Let a>0 and b>1 be constants, and let f .n/ be a function defined over real numbers n1. Then the recurrence

(

‚.1/ if 0හn<1;

T .n/ D

aT .n=b/ C f .n/ if n1

has solution

blogXb nc logb a/C

T.n/ D‚.n ajf.n=bj/: (4.18) j D0

Proof Consider the recursion tree in Figure 4.3. Let’s look ûrst at its inter

nal nodes. The root of the tree has cost f .n/, and it has a children, each with cost f .n=b/. (It is convenient to think of a as being an integer, especially when visualizing the recursion tree, but the mathematics does not require it.) Each of thesechildren has a children, making a2 nodes at depth 2, and each of the a children has cost f .n=b2/. In general, there are aj nodes at depth j , and each node has cost f .n=bj /.

Now, let’s move on to understanding the leaves. The tree grows downward un

til n=bj becomes less than 1. Thus, the tree has height blogbncC 1, because n=bblogb nc  n=blogbn D1 and n=bblogb ncC1 <n=b logbn D1. Since, as we have observed, the number of nodes at depth j is aj and all the leaves are at depth blogbnc C 1, the tree contains ablogb ncC1 leaves. Using the identity (3.21) on page 66, we have ablogb ncC1 හ alogb nC1 D anlogba DO.nlogb a/, since a is constant, and ablogb ncC1  alogbn D nlogba DY.nlogb a/. Consequently, the total number of leaves is ‚.nlogb a/4asymptotically, the watershed function.

We are now in a position to derive equation (4.18) by summing the costs of the nodes at each depth in the tree, as shown in the ûgure. The ûrst term in the equation is the total costs of the leaves. Since each leaf is at depth blogbnc C 1 and n=bblogb ncC1 < 1, the base case of the recurrence gives the cost of a leaf: T .n=bblogb ncC1/ D ‚.1/. Hence the cost of all ‚.nlogb a/ leaves is ‚.nlogb a/  ‚.1/ D ‚.nlogb a/ by Problem 3-5(d). The second term in equation (4.18) is the cost of the internal nodes, which, in the underlying divide-and

conquer algorithm, represents the costs of dividing problems into subproblems and

## 4.6 Proof of the continuous master theorem f .n/ f .n/

a f .n=b/ f .n=b/ … f .n=b/ af .n=b/ aa a

blogb nc C 1

…… …

f.n=b2/f.n=b2/ f.n=b2/ f.n=b2/f.n=b2/ f.n=b2/ f.n=b2/f.n=b2/ f.n=b2/ a2f.n=b2/

……………………… … aaaaaaaaa ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ ‚.1/ … ‚.1/ ‚.1/ ‚.1/ ‚.nlogb a/

ablogb ncC1

blogXb nc logb a/C

Total: ‚.n ajf.n=bj/ j D0

Figure4.3 The recursion tree generated by T .n/ D aT .n=b/ C f .n/. The tree isa complete a-ary tree with ablogb ncC1 leaves and height blogb ncC 1. The cost of the nodes at each depth is shown

at the right, and their sum is given in equation (4.18).

then recombining the subproblems. Since the cost for all the internal nodes at depth j is aj f .n=bj /, the total cost of all internal nodes is blogXb nc ajf.n=bj/ : j D0

As we’ll see, the three cases of the master theorem depend on the distribution of the total cost across levels of the recursion tree:

Case 1: The costs increase geometrically from the root to the leaves, growing bya constant factor with each level.

Case 2: The costs depend on the value of k in the theorem. With kD0, the costs are equal for each level; with kD1, the costs grow linearly from the root to the leaves; with kD2, the growth is quadratic; and in general, the costs grow polynomially in k.

Case 3: The costs decrease geometrically from the root to the leaves, shrinking by a constant factor with each level.

The summation in equation (4.18) describes the cost of the dividing and com

bining steps in the underlying divide-and-conquer algorithm. The next lemma pro

vides asymptotic bounds on the summation’s growth.

Lemma 4.3

Let a>0 and b>1 be constants, and let f .n/ be a function defined over real numbers n1. Then the asymptotic behavior of the function

blogXb nc

g.n/ D ajf.n=bj/ ; (4.19) j D0

defined for n1, can be characterized as follows:

1. If there exists a constant >0 such that f .n/ D O.nlogb a/, then g.n/ D O.nlogb a/. 2. If there exists a constant k0 such that f .n/ D ‚.nlogba lgk n/, then g.n/ D ‚.nlogba lgkC1 n/. 3. If there exists a constant c in the range 0<c<1 such that 0<af .n=b/ හ cf .n/ for all n1, then g.n/ D ‚.f .n//. Proof For case 1, we have f .n/ D O.nlogb a/, which implies that f.n=bj/ D O..n=bj / logb a/. Substituting into equation (4.19) yields

blogXbnc Î Ï

Ílogb a

n

g.n/ D ajO bj

j D0

blogXb nc

 Ílogb a!

jn

DO abj (by Problem 3-5(c), repeatedly)

j D0

!

blogXb ncÎ ab Ïjlogb a

DO n

blogba

j D0

!

blogXb nc logb a

D O n .b/j (by equation (3.17) on page 66) j D0

ÎÎ ÏÏ

b.blogb ncC1/  1logb a

DO n (by equation (A.6) on page 1142) ,

b 1

the last series being geometric. Since b and � are constants, the b 1 denominator doesn’t affect the asymptotic growth of g.n/, and neither does the 1 in

## 4.6 Proof of the continuous master theorem 111 the numerator. Since b.blogb ncC1/ හ .blogb nC1/ D bn D O.n/, we obtain g.n/ D O.nlogb a  O.n// D O.nlogb a/, thereby proving case 1.

Case 2 assumes that f .n/ D ‚.nlogba lgk n/, from which we can conclude that f.n=bj/ D ‚..n=bj/ logba lgk.n=bj //. Substituting into equation (4.19) and repeatedly applying Problem 3-5(c) yields

blogXbnc  Í!

Ílogba

nn

g.n/ D‚ aj lgk

bj bjj D0

blogXbnc aj Í!



logba nD‚n bj logba lgk bjj D0

blogXbnc  Í! logba n

D‚ n lgk bj

j D0

blogXb nc Ïk!

Î logb.n=bj /

logba

D‚ n (by equation (3.19) on page 66) j D0 logb2

blogXb nc Ïk! logba Î logbnj (by equations (3.17), (3.18),

D‚ n

j D0 logb2 and (3.20))

!

blogXb nc

nlogba D‚ .logb n  j/k logkb2 jD0

!

blogXb nc logba

D‚n .logb nj/k (b>1 and k are constants) . j D0

The summation within the ‚-notation can be bounded from above as follows:

blogXbnc blogXb nc

.logbnj/k හ .blogb nc C 1  j/k

jD0 jD0

blogb ncC1

X

D jk (reindexing4pages 114331144) j D1

D O..blogb nc C 1/kC1/ (by Exercise A.1-5 on page 1144)

D O.logkbC1 n/ (by Exercise 3.3-3 on page 70) .

Exercise 4.6-1 asks you to show that the summation can similarly be bounded from below by Y.logkC1 n/. Since we have tight upper and lower bounds, the summa

b

ã logba logkC1 ätion is ‚.logkbC1 n/, from which we can conclude that g.n/ D‚ n n ,

b

thereby completing the proof of case 2.

For case 3, observe that f .n/ appears in the deûnition (4.19) of g.n/ (when j D0) and that all terms of g.n/ are positive. Therefore, we must have g.n/ D

Y.f.n// , and it only remains to prove that g.n/ D O.f .n//. Performing j iterations of the inequality af .n=b/ හ cf .n/ yields ajf.n=bj/ හ cjf.n/. Substituting into equation (4.19), we obtain blogXb nc

g.n/ D ajf.n=bj/

j D0

blogXb nc

හ cjf.n/ j D0

X

හ f.n/ cj j D0

ÎÏ

D f.n/ 1 (by equation (A.7) on page 1142 since jcj < 1)

1c D O.f .n// :

Thus, we can conclude that g.n/ D ‚.f .n//. With case 3 proved, the entire proof of the lemma is complete.

We can now state and prove the continuous master theorem.

Theorem 4.4 (Continuous master theorem)

Let a>0 and b>1 be constants, and let f .n/ be a driving function that is defined and nonnegative on all sufficiently large reals. Deûne the algorithmic recurrence T .n/ on the positive real numbers by

T.n/ D aT.n=b/ Cf.n/:

Then the asymptotic behavior of T .n/ can be characterized as follows:

1. If there exists a constant >0 such that f .n/ D O.nlogb a/, then T .n/ D logb a/. ‚.n

2. If there exists a constant k0 such that f .n/ D ‚.nlogba lgk n/, then T .n/ D ‚.nlogba lgkC1 n/. 3. If there exists a constant >0 such that f .n/ D Y.nlogb aC/, and if f .n/ additionally satisfies the regularity condition af .n=b/ හ cf .n/ for some constant c<1 and all sufficiently large n, then T .n/ D ‚.f .n//. Proof The idea is to bound the summation (4.18) from Lemma 4.2 by applying Lemma 4.3. But we must account for Lemma 4.2 using a base case for 0< n<1,

## 4.6 Proof of the continuous master theorem 113 whereas this theorem uses an implicit base case for 0 < n < n0, where n0 >0 is an arbitrary threshold constant. Since the recurrence is algorithmic, we can assume that f .n/ is defined for n  n0.

For n>0, let us deûne two auxiliary functions T 0.n/ D T .n0 n/ and f 0.n/ D f .n0 n/. We have

T 0.n/ D T .n0 n/

(

D ‚.1/ if n0n < n0 ;

aT.n0 n=b/ C f.n0 n/ if n0n  n0

(

‚.1/ if n<1;

D (4.20)

aT 0.n=b/ C f 0.n/ if n1:

Wehave obtained arecurrence for T 0.n/ that satisfies the conditions of Lemma4.2, and by that lemma, the solution is

blogXb nc logb a/C

T 0.n/ D ‚.n ajf 0.n=bj/ : (4.21) j D0

To solve T 0.n/, we ûrst need to bound f 0.n/. Let’s examine the individual cases in the theorem.

The condition for case 1 is f .n/ D O.nlogb a/ for some constant >0. We have

f 0.n/ D f .n0 n/

D O..n0 n/ logb a/

D O.nlogb a/ ;

since a, b, n0, and � are all constant. The function f 0.n/ satisfies the conditions of case1ofLemma4.3, andthesummation inequation (4.18) ofLemma4.2evaluates

to O.nlogb a/. Because a, b and n0 are all constants, we have

T .n/ D T 0.n=n0/

D ‚..n=n0/ logb a/ C O..n=n0/ logb a/

D ‚.nlogb a/ C O.nlogb a/logb a/

D ‚.n (by Problem 3-5(b)) ,

thereby completing case 1 of the theorem.

The condition for case 2 is f .n/ D ‚.nlogba lgk n/ for some constant k0. We have

f 0.n/ D f .n0 n/

D ‚..n0 n/ logba lgk.n0 n// logba lgk n/

D ‚.n (by eliminating the constant terms) .

Similar to the proof of case 1, the function f 0.n/ satisfies the conditions of case 2 of Lemma 4.3. The summation in equation (4.18) of Lemma 4.2 is therefore ‚.nlogba lgkC1 n/, which implies that

T .n/ D T 0.n=n0/ D ‚..n=n0/ logb a/ C ‚..n=n0/ logba lgkC1.n=n0// logba lgkC1 n/

D ‚.nlogb a/ C ‚.n logba lgkC1 n/

D ‚.n (by Problem 3-5(c)) ,

which proves case 2 of the theorem.

Finally, the condition for case 3 is f .n/ D Y.nlogb aC/ for some constant >0 and f .n/ additionally satisfies the regularity condition af .n=b/ හ cf .n/ for all n  n0 and some constants c<1 and n0 > 1. The ûrst part of case 3 is like case 1:

f 0.n/ D f .n0 n/ D Y..n0 n/ logb aC/ D Y.nlogb aC/ :

Using the deûnition of f 0.n/ and the fact that n0n  n0 for all n1, we have for n1 that af 0.n=b/ D af .n0 n=b/ හ cf .n0 n/

D cf 0.n/ : Thus f 0.n/ satisfies the requirements for case 3 of Lemma 4.3, and the summation in equation (4.18) of Lemma 4.2 evaluates to ‚.f 0.n//, yielding

T .n/ D T 0.n=n0/ D ‚..n=n0/ logb a/ C ‚.f 0.n=n0// D ‚.f 0.n=n0// D ‚.f .n// ;

which completes the proof of case 3 of the theorem and thus the whole theorem.

## Exercises

4.6-1

Show that Pblogb nc.logbnj/k DY.logkC1 n/.

jD0 b

? 4.6-2

Show that case 3 of the master theorem is overstated (which is also why case 3 of Lemma 4.3 does not require that f .n/ D Y.nlogb aC/) in the sense that the

## 4.7 Akra-Bazzi recurrences regularity condition af .n=b/ හ cf .n/ for some constant c<1 implies that there exists a constant >0 such that f .n/ D Y.nlogb aC/.

? 4.6-3 For f .n/ D ‚.nlogb a= lgn/, prove that the summation in equation (4.19) has solution g.n/ D ‚.nlogba lglgn/. Conclude that a master recurrence T .n/ using f .n/ as its driving function has solution T .n/ D ‚.nlogba lglgn/.

## 4.7 Akra-Bazzi recurrences

This section provides an overview of two advanced topics related to divide-and

conquer recurrences. The ûrst deals with technicalities arising from the use of

üoors and ceilings, and the second discusses the Akra-Bazzi method, which in

volves a little calculus, for solving complicated divide-and-conquer recurrences. In particular, we’ll look at the class of algorithmic divide-and-conquer recur

rences originally studied by M. Akra and L. Bazzi [13]. These Akra-Bazzi recur

rences take the form

k

X

T.n/ Df.n/ C aiT.n=bi/; (4.22) iD1

where k is a positive integer; all the constants a1;a2;:::;ak 2 R are strictly positive; all the constants b1;b2;:::;bk 2 R are strictly greater than 1; and the driving function f .n/ is defined on sufficiently large nonnegative reals and is itself nonnegative.

Akra-Bazzi recurrences generalize the class of recurrences addressed by the master theorem. Whereas master recurrences characterize the running times of

divide-and-conquer algorithms that break a problem into equal-sized subproblems(modulo üoors and ceilings), Akra-Bazzi recurrences can describe the running time of divide-and-conquer algorithms that break a problem into different-sized subproblems. The master theorem, however, allows you to ignore üoors and ceilings, but the Akra-Bazzi method for solving Akra-Bazzi recurrences needs an additional requirement to deal with üoors and ceilings.

But before diving into the Akra-Bazzi method itself, let’s understand the lim

itations involved in ignoring üoors and ceilings in Akra-Bazzi recurrences. As

you’re aware, algorithms generally deal with integer-sized inputs. The mathemat

ics for recurrences is often easier with real numbers, however, than with integers,

where we must cope with üoors and ceilings to ensure that terms are well defined. The difference may not seem to be much4especially because that’s often the truthwith recurrences4but to be mathematically correct, we must be careful with our

assumptions. Since our end goal is to understand algorithms and not the vagaries of mathematical corner cases, we’d like to be casual yet rigorous. How can we treat üoors and ceilings casually while still ensuring rigor?

From a mathematical point of view, the difûculty in dealing with üoors and ceilings isthat somedriving functions canbereally, reallyweird. Soit’snotokay in general to ignore üoors and ceilings in Akra-Bazzi recurrences. Fortunately, mostof the driving functions we encounter in the study of algorithms behave nicely, andüoors and ceilings don’t make a difference.

## The polynomial-growth condition

If the driving function f .n/ in equation (4.22) is well behaved in the following sense, it’s okay to drop üoors and ceilings.

A function f .n/ defined on all sufficiently large positive reals satisfies thepolynomial-growth condition if there exists a constant ny > 0 such that the following holds: for every constant 1, there exists a constant d >1 (depending on ) such that f.n/=d හ f.n/ හ df.n/ for all 1හ හ� and n yn.

This deûnition may be one of the hardest in this textbook to get your head around. To a ûrst order, it says that f .n/ satisfies the property that f .‚.n// D ‚.f .n//, although the polynomial-growth condition is actually somewhat stronger (see Exercise 4.7-4). The deûnition also implies that f .n/ is asymptotically positive (see Exercise 4.7-3).

Examples of functions that satisfy the polynomial-growth condition include any function of the form f .n/ D ‚.n˛ lgˇn lglgn/, where ˛, ˇ, and � are constants. Mostof thepolynomially bounded functions used inthis book satisfy the condition.

Exponentials and superexponentials do not (see Exercise 4.7-2, for example), and

there also exist polynomially bounded functions that do not.

## Floors and ceilings in "nice" recurrences

When the driving function in an Akra-Bazzi recurrence satisfies the polynomial- growth condition, üoors and ceilings don’t change the asymptotic behavior of the solution. The following theorem, which is presented without proof, formalizes this notion.

Theorem 4.5

Let T .n/ be a function defined on the nonnegative reals that satisfies recurrence (4.22), where f .n/ satisfies the polynomial-growth condition. Let T 0.n/ be another function defined on the natural numbers also satisfying recurrence (4.22),

## 4.7 Akra-Bazzi recurrences 117 except that each T .n=bi/ is replaced either with T .dn=bie/ or with T .bn=bic/. Then we have T 0.n/ D ‚.T .n//.

Floors and ceilings represent a minor perturbation to the arguments in the recursion. By inequality (3.2) on page 64, they perturb an argument by at most 1. But much larger perturbations are tolerable. As long as the driving function f .n/in recurrence (4.22) satisfies the polynomial-growth condition, it turns out that replacing any term T .n=bi/ with T.n=bi C hi.n//, where jhi.n/j D O.n= lg1C n/ for some constant >0 and sufficiently large n, leaves the asymptotic solution unaffected. Thus, the divide step in a divide-and-conquer algorithm can be moderately coarse without affecting the solution to its running-time recurrence.

## The Akra-Bazzi method

The Akra-Bazzi method, not surprisingly, was developed to solve Akra-Bazzi recurrences (4.22), which by dint of Theorem 4.5, applies in the presence of üoors

and ceilings or even larger perturbations, as just discussed. The method involves ûrst determining the unique real number p such that PkiD1ai=bp D 1. Such a p

i

always exists, because when p !1, the sum goes to 1; it decreases as p increases; and when p!1, it goes to 0. The Akra-Bazzi method then gives the solution to the recurrence as

ÎÎZn ÏÏ

np f.x/ T.n/ D‚ 1C dx : (4.23)

1 xpC1

As an example, consider the recurrence

T.n/ D T.n=5/ CT.7n=10/ Cn : (4.24)

We’ll see the similar recurrence (9.1) on page 240 when we study an algorithm for selecting the ith smallest element from a set of n numbers. This recurrence has the form of equation (4.22), where a1 D a2 D 1, b1 D 5, b2 D 10=7, and f.n/ D n. To solve it, the Akra-Bazzi method says that we should determine the unique psatisfying

Î1Ïp Î7Ïp C D1:

5 10

Solving for p is kind of messy4it turns out that p D 0:83978 : : :4but we can solve the recurrence without actually knowing the exact value for p. Observe that .1=5/0 C .7=10/0 D 2 and .1=5/1 C .7=10/1 D 9=10, and thus p lies in the range 0<p<1. That turns out to be sufûcient for the Akra-Bazzi method to give us the solution. We’ll use the fact from calculus that if k ¤ 1, then R xkdx DxkC1=.k C1/, which we’ll apply with k Dp¤1. The Akra-Bazzi

solution (4.23) gives us

ÎÎZ ÏÏ

n f .x/

T.n/ D‚ np 1C dx 1 xpC1

ÎÎZn ÏÏ

D ‚ np 1C xpdx

Î Î Ð1 nÏÏ

x1pD‚np 1C

1p

ÎÎÎ 1 ÏÏÏ

n1p

D‚np1C 

1p 1p D ‚ ãnp‚.n1p/ ä (because 1p is a positive constant) D ‚.n/ (by Problem 3-5(d)) .

Although the Akra-Bazzi method is more general than the master theorem, it requires calculus and sometimes a bit more reasoning. You also must ensure that

your driving function satisfies the polynomial-growth condition if you want to ignore üoors and ceilings, although that’s rarely a problem. When it applies, the master method is much simpler to use, but only when subproblem sizes are moreor less equal. They are both good tools for your algorithmic toolkit.

## Exercises

? 4.7-1

Consider an Akra-Bazzi recurrence T .n/ on the reals as given in recurrence (4.22), and deûne T 0.n/ as

k

X

T0.n/ Dcf.n/ C aiT0.n=bi/; i D1

where c>0 isconstant. Provethatwhatevertheimplicitinitialconditionsfor T .n/ might be, there exist initial conditions for T 0.n/ such that T 0.n/ D cT .n/ for all n>0. Conclude that we can drop the asymptotics on a driving function in anyAkra-Bazzi recurrence without affecting its asymptotic solution.

4.7-2

Showthat f .n/ D n2 satisfiesthepolynomial-growth condition but that f .n/ D 2n does not.

4.7-3

Let f .n/ be a function that satisfies the polynomial-growth condition. Prove that f .n/ is asymptotically positive, that is, there exists a constant n0 0 such that f.n/  0 for all n  n0.

## Problems for Chapter 4

? 4.7-4 Give an example of a function f .n/ that does not satisfy the polynomial-growth condition but for which f .‚.n// D ‚.f .n//.

4.7-5

Use the Akra-Bazzi method to solve the following recurrences.

a. T.n/ D T.n=2/ CT.n=3/ CT.n=6/ Cn lgn. b. T .n/ D 3T .n=3/ C 8T .n=4/ C n2= lgn. c. T .n/ D .2=3/T .n=3/ C .1=3/T .2n=3/ C lgn. d. T .n/ D .1=3/T .n=3/ C 1=n. e. T .n/ D 3T .n=3/ C 3T .2n=3/ C n2. ? 4.7-6

Use the Akra-Bazzi method to prove the continuous master theorem.

Problems

4-1 Recurrence examples

Giveasymptotically tight upper and lowerbounds for T .n/ in each of thefollowing algorithmic recurrences. Justify your answers.

a. T .n/ D 2T .n=2/ C n3. b. T .n/ D T .8n=11/ C n. c. T .n/ D 16T .n=4/ C n2. d. T .n/ D 4T .n=2/ C n2 lgn. e. T .n/ D 8T .n=3/ C n2. f. T .n/ D 7T .n=2/ C n2 lgn. p

g. T.n/ D2T.n=4/ C n. h. T.n/ D T.n 2/ Cn2.

4-2 Parameter-passing costs

Throughout this book, we assume that parameter passing during procedure calls takes constant time, even if an N -element array is being passed. This assumptionis valid in most systems because a pointer to the array is passed, not the array itself. This problem examines the implications of three parameter-passing strategies:

1. Arrays are passed by pointer. Time D ‚.1/. 2. Arrays are passed by copying. Time D ‚.N /, where N is the size of the array. 3. Arrays are passed by copying only the subrange that might be accessed by the called procedure. Time D ‚.n/ if the subarray contains n elements. Consider the following three algorithms:

a. The recursive binary-search algorithm for ûnding a number in a sorted array (see Exercise 2.3-6). b. The MERGE-SORT procedure from Section 2.3.1. c. The MATRIX-MULTIPLY-RECURSIVE procedure from Section 4.1. Give nine recurrences Ta1.N; n/; Ta2.N; n/; : : : ; Tc3.N; n/ for the worst-case run

ning times of each of the three algorithms above when arrays and matrices are

passed using each of the three parameter-passing strategies above. Solve your re

currences, giving tight asymptotic bounds.

4-3 Solving recurrences with a change of variables

Sometimes, a little algebraic manipulation can make an unknown recurrence similar to one you have seen before. Let’s solve the recurrence

ãp ä

T.n/ D2T n C‚.lgn/ (4.25)

by using the change-of-variables method.

a. Deûne mD lgn and S.m/ D T .2m/. Rewrite recurrence (4.25) in terms of m and S.m/. b. Solve your recurrence for S.m/. c. Use your solution for S.m/ to conclude that T .n/ D ‚.lgn lglgn/. d. Sketch the recursion tree for recurrence (4.25), and use it to explain intuitively why the solution is T .n/ D ‚.lgn lglgn/. Solve the following recurrences by changing variables:

## Problems for Chapter 4

p

e. T.n/ D2T. n/ C‚.1/. p f. T.n/ D3T. 3n/ C‚.n/. 4-4 More recurrence examples

Giveasymptotically tight upper and lowerbounds for T .n/ in each of thefollowing recurrences. Justify your answers.

a. T.n/ D 5T.n=3/ Cn lgn. b. T .n/ D 3T .n=3/ C n= lgn. p c. T.n/ D8T.n=2/ Cn3 n. d. T.n/ D 2T.n=2 2/ Cn=2. e. T .n/ D 2T .n=2/ C n= lgn. f. T.n/ D T.n=2/ CT.n=4/ CT.n=8/ Cn. g. T.n/ D T.n 1/ C1=n. h. T.n/ D T.n 1/ C lgn. i. T.n/ D T.n 2/ C1= lgn. pp j. T.n/ D nT. n/ Cn. 4-5 Fibonacci numbers

This problem develops properties of the Fibonacci numbers, which are defined by recurrence (3.31) on page 69. We’ll explore the technique of generating functions to solve the Fibonacci recurrence. Deûne the generating function (or formal power series) F as

X

F .´/ D Fi´i

iD0

D 0C´C´2C2´3C3´4C5´5C8´6C13´7C21´8C ;

where Fi is the ith Fibonacci number.

a. Show that F.´/ D ´C´F.´/ C´2F.´/.

b. Show that ´

F .´/ D

1  ´  ´2 ´

D .1 ´/.1  y

´/

ÎÏ

11 1

Dp ;

5 1´ ´

1 y

where � is the golden ratio, and y is its conjugate (see page 69).

c. Show that X

F .´/ D p .i  yi/´i : iD0 5

Youmay usewithout proof thegenerating-function version ofequation (A.7)onpage 1142, P1kD0xk D1=.1 x/. Because this equation involves a generating function, x is a formal variable, not a real-valued variable, so that you don’t have to worry about convergence of the summation or about the requirement in

equation (A.7) that jxj < 1, which doesn’t make sense here. p

d. Use part (c) to prove that Fi Di= 5 for i >0, rounded to the nearest integer. (Hint: Observe that ˇˇ yˇˇ < 1.)

e. Prove that FiC2  i for i0. 4-6 Chip testing

Professor Diogenes has n supposedly identical integrated-circuit chips that in principle are capable of testing each other. The professor’s test jig accommodates two chips at atime. Whenthejig isloaded, each chip tests theother andreports whetherit is good or bad. A good chip always reports accurately whether the other chip isgood or bad, but the professor cannot trust the answer of a bad chip. Thus, the four possible outcomes of a test are as follows:

Chip A says Chip B says Conclusion B is good A is good both are good, or both are bad B is good A is bad at least one is bad B is bad A is good at least one is bad B is bad A is bad at least one is bad

a. Show that if at least n=2 chips are bad, the professor cannot necessarily determine which chips are good using any strategy based on this kind of pairwise test. Assume that the bad chips can conspire to fool the professor.

## Problems for Chapter 4

Now you will design an algorithm to identify which chips are good and which arebad, assuming that more than n=2 of the chips are good. First, you will determine how to identify one good chip.

b. Show that bn=2c pairwise tests are sufûcient to reduce the problem to one of nearly half the size. That is, show how to use bn=2c pairwise tests to obtain a set with at most dn=2e chips that still has the property that more than half of the chips are good. c. Show how to apply the solution to part (b) recursively to identify one good chip. Give and solve the recurrence that describes the number of tests needed to identify one good chip. You have now determined how to identify one good chip.

d. Show how to identify all the good chips with an additional ‚.n/ pairwise tests. 4-7 Monge arrays An mn array A of real numbers is a Monge array if for all i, j , k, and l such that 1හi <k හm and 1හj <l හn, we have

AOEi;j� CAOEk;l� හ AOEi;l� CAOEk;j� :

In other words, whenever we pick two rows and two columns of a Monge array andconsider the four elements atthe intersections of the rowsand the columns, the sumof the upper-left and lower-right elements is less than or equal to the sum of the lower-left and upper-right elements. For example, the following array is Monge:

10 17 13 28 23 17 22 16 29 23 24 28 22 34 24 11 13 6 17 7 45 44 32 37 23 36 33 19 21 6 75 66 51 53 34

a. Prove that an array is Monge if and only if for all i D 1;2;:::;m  1 and j D1;2;:::;n 1, we have AOEi;j� CAOEi C1;j C1� හAOEi;j C1� CAOEi C1;jc:

(Hint: For the <if= part, use induction separately on rows and columns.)

b. The following array is not Monge. Change one element in order to make it Monge. (Hint: Use part (a).)

37 23 22 32 21 6 710 53 34 30 31 32 13 9 6 43 21 15 8

c. Let f .i/ be the index of the column containing the leftmost minimum element of row i. Prove that f.1/ හ f.2/ හ  හ f.m/ for any mn Monge array. d. Here is a description of a divide-and-conquer algorithm that computes the leftmost minimum element in each row of an mn Monge array A:

Construct asubmatrix A0 of A consisting of theeven-numbered rowsof A. Recursively determine the leftmost minimum for each row of A0. Then compute the leftmost minimum in the odd-numbered rows of A.

Explain how to compute the leftmost minimum in the odd-numbered rows of A (given that the leftmost minimum of the even-numbered rows is known) in

O.m C n/ time. e. Write the recurrence for the running time of the algorithm in part (d). Show that its solution is O.m C n logm/. Chapter notes

Divide-and-conquer as a technique for designing algorithms dates back at least to 1962 in an article by Karatsuba and Ofman [242], but it might have been used well before then. According to Heideman, Johnson, and Burrus [211], C. F. Gauss devised the ûrst fast Fourier transform algorithm in 1805, and Gauss’s formulation

breaks the problem into smaller subproblems whose solutions are combined.

Strassen’s algorithm [424] caused much excitement when it appeared in 1969.

Beforethen, fewimagined thepossibility ofanalgorithm asymptotically faster thanthe basic MATRIX-MULTIPLY procedure. Shortly thereafter, S. Winograd reduced the number of submatrix additions from 18 to 15 while still using seven submatrix multiplications. This improvement, which Winograd apparently never published (and which is frequently miscited in the literature), may enhance the practicality of the method, but it does not affect its asymptotic performance. Probert [368] described Winograd’s algorithm and showed that with seven multiplications, 15

additions is the minimum possible.

Strassen’s ‚.nlg7/ D O.n2:81/ bound for matrix multiplication held until 1987, when Coppersmith and Winograd [103] made a signiûcant advance, improving the

## Notes for Chapter 4

bound to O.n2:376/ time with a mathematically sophisticated but wildly impractical algorithm based on tensor products. It took approximately 25 years before the asymptotic upper bound was again improved. In 2012 Vassilevska Williams [445] improved it to O.n2:37287/, and two years later Le Gall [278] achieved O.n2:37286/, both ofthem using mathematically fascinating but impractical algorithms. The best lower bound to date is just the obvious Y.n2/ bound (obvious because any algorithm for matrix multiplication must ûll in the n2 elements of the product matrix).

The performance of MATRIX-MULTIPLY-RECURSIVE can be improved in practice by coarsening the leaves of the recursion. It also exhibits better cache behavior than MATRIX-MULTIPLY, although MATRIX-MULTIPLY can be improved by <tiling.= Leiserson et al. [293] conducted a performance-engineering study of matrix multiplication in which aparallel and vectorized divide-and-conquer algorithm achieved the highest performance. Strassen’s algorithm can be practical for largedense matrices, although large matrices tend to be sparse, and sparse methods canbe much faster. When using limited-precision üoating-point values, Strassen’s algorithm produces larger numerical errors than the ‚.n3/ algorithms do, althoughHigham [215] demonstrated that Strassen’s algorithm is amply accurate for some applications.

Recurrences were studied as early as 1202 by Leonardo Bonacci [66], also known as Fibonacci, for whom the Fibonacci numbers are named, although Indianmathematicians had discovered Fibonacci numbers centuries before. The French mathematician De Moivre [108] introduced the method of generating functions with which he studied Fibonacci numbers (see Problem 4-5). Knuth [259] and Liu [302] are good resources for learning the method of generating functions.

Aho, Hopcroft, and Ullman [5, 6] offered one of the ûrst general methods for solving recurrences arising from the analysis of divide-and-conquer algorithms. The master method was adapted from Bentley, Haken, and Saxe [52]. The Akra- Bazzi method is due (unsurprisingly) to Akra and Bazzi [13]. Divide-and-conquer recurrences have been studied by many researchers, including Campbell [79], Graham, Knuth, and Patashnik [199], Kuszmaul and Leiserson [274], Leighton [287], Purdom and Brown [371], Roura [389], Verma [447], and Yap [462].

The issue of üoors and ceilings in divide-and-conquer recurrences, including a theorem similar to Theorem 4.5, was studied by Leighton [287]. Leighton proposed a version of the polynomial-growth condition. Campbell [79] removed several limitations in Leighton’s statement of it and showed that there were polynomially bounded functions that do not satisfy Leighton’s condition. Campbell also carefully studied many other technical issues, including the well-definedness of divide-and-conquer recurrences. Kuszmaul and Leiserson [274] provided a proofof Theorem 4.5 that does not involve calculus or other higher math. Both Campbell and Leighton explored the perturbations of arguments beyond simple üoors and ceilings.