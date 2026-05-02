# Chapter 4: Divide-and-Conquer

For the divide-and-conquer matrix-multiplication algorithms presented in Sections 4.1 and 4.2, we’ll derive recurrences that describe their worst-case running times. To understand why these two divide-and-conquer algorithms perform the way they do, you’ll need to learn how to solve the recurrences that describe their running times. Sections 4.3–4.7 teach several methods for solving recurrences. These sections also explore the mathematics behind recurrences, which can give you stronger intuition for designing your own divide-and-conquer algorithms.

We want to get to the algorithms as soon as possible. So, let’s just cover a few recurrence basics now, and then we’ll look more deeply at recurrences, especially how to solve them, after we see the matrix-multiplication examples.

The general form of a recurrence is an equation or inequality that describes a function over the integers or reals using the function itself. It contains two or more cases, depending on the argument. If a case involves the recursive invocation of the function on different (usually smaller) inputs, it is a recursive case. If a case does not involve a recursive invocation, it is a base case. There may be zero, one, or many functions that satisfy the statement of the recurrence. The recurrence is well defined if there is at least one function that satisfies it, and ill defined otherwise.

## Algorithmic recurrences

We’ll be particularly interested in recurrences that describe the running times of divide-and-conquer algorithms. A recurrence T .n/ is algorithmic if, for every sufficiently large threshold constant n0 >0, the following two properties hold:

Line 1.: For all n < n0, we have T .n/ D ‚.1/. 2. For all n  n0, every path of recursion terminates in a defined base case within a finite number of recursive invocations. Similar to how we sometimes abuse asymptotic notation (see page 60), when a function is not defined for all arguments, we understand that this deûnition is constrained to values of n for which T .n/ is defined.

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

Line 1: for i D1 to n // compute entries in each of n rows

Line 2: for j D1 to n // compute n entries in row i

Line 3: for kD1 to n

Line 4: cij Dcij Caik bkj // add in another term of equation (4.1)

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

Line 1: if n == 1

Line 2: // Base case.

Line 3: c11 Dc11 Ca11 b11

Line 4: return

Line 5: // Divide.

Line 6: partition A, B, and C into n=2  n=2 submatrices

A11; A12; A21; A22; B11; B12; B21; B22;

and C11; C12; C21; C22; respectively

Line 7: // Conquer.

Line 8: MATRIX-MULTIPLY-RECURSIVE.A11; B11; C11; n=2/ 9 MATRIX-MULTIPLY-RECURSIVE.A11; B12; C12; n=2/ 10 MATRIX-MULTIPLY-RECURSIVE.A21; B11; C21; n=2/ 11 MATRIX-MULTIPLY-RECURSIVE.A21; B12; C22; n=2/ 12 MATRIX-MULTIPLY-RECURSIVE.A12; B21; C11; n=2/ 13 MATRIX-MULTIPLY-RECURSIVE.A12; B22; C12; n=2/ 14 MATRIX-MULTIPLY-RECURSIVE.A22; B21; C21; n=2/ 15 MATRIX-MULTIPLY-RECURSIVE.A22; B22; C22; n=2/

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

Line 1.: If nD1, the matrices each contain a single element. Perform a single scalarmultiplication and a single scalar addition, as in line 3 of MATRIX-MULTIPLYRECURSIVE, taking ‚.1/ time, and return. Otherwise, partition the input matrices A and B and output matrix C into n=2  n=2 submatrices, as in equation (4.2). This step takes ‚.1/ time by index calculation, just as in MATRIXMULTIPLY- RECURSIVE. 2. Create n=2  n=2 matrices S1; S2; : : : ; S10, each of which is the sum or difference of two submatrices from step 1. Create and zero the entries of seven n=2  n=2 matrices P1; P2; : : : ; P7 to hold seven n=2  n=2 matrix products. All 17 matrices can be created, and the Pi initialized, in ‚.n2/ time. 3. Using the submatrices from step 1 and the matrices S1; S2; : : : ; S10 created in step 2, recursively compute each of the seven matrix products P1; P2; : : : ; P7, taking 7T .n=2/ time. 4. Update the four submatrices C11; C12; C21; C22 ofthe result matrix C by adding or subtracting various Pi matrices, which takes ‚.n2/ time.

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

Line 13: 68

:

Line 75: 42

Show your work.

