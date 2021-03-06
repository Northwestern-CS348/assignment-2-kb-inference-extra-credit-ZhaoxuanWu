import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

        if not isinstance(fact_or_rule, Fact) and not isinstance(fact_or_rule, Rule):
            print("Only retracting a Fact or a Rule is allowed")
            return
        if isinstance(fact_or_rule, Rule):
            for rule in self.rules:
                if rule == fact_or_rule:
                    fact_or_rule = rule
                    break
            else:
                print('Rule not present')
                return
        elif isinstance(fact_or_rule, Fact):
            for fact in self.facts:
                if fact == fact_or_rule:
                    fact_or_rule = fact
                    break
            else:
                print('Fact not present')
                return
        if fact_or_rule.supported_by:
            print("Cannot retract a supported fact or rule:", fact_or_rule)
            return
        if isinstance(fact_or_rule, Rule) and fact_or_rule.asserted:
            print("Cannot retract an asserted rule")
            return
        self.facts.remove(fact_or_rule) if isinstance(fact_or_rule, Fact) else self.rules.remove(fact_or_rule)
        for fact in fact_or_rule.supports_facts:
            print(fact_or_rule, 'supports each fact', fact)
            for pair in fact.supported_by:
                if fact_or_rule in pair:
                    self._get_fact(fact).supported_by.remove(pair)
                    # print("new Fact after removing", fact)
            self.kb_retract(fact)
        for rule in fact_or_rule.supports_rules:
            print(fact_or_rule, 'supports each rule', rule)
            for pair in rule.supported_by:
                if fact_or_rule in pair:
                    self._get_rule(rule).supported_by.remove(pair)
            self.kb_retract(rule)


    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        print(self.kb_explain_helper(fact_or_rule, 0))
        return self.kb_explain_helper(fact_or_rule, 0)


    def kb_explain_helper(self, fact_or_rule, level):
        output = ""
        if not isinstance(fact_or_rule, Fact) and not isinstance(fact_or_rule, Rule):
            print("Only explaining a Fact or a Rule is allowed")
            return False
        if isinstance(fact_or_rule, Rule):
            found_rule = self._get_rule(fact_or_rule)
            if not found_rule:
                return "Rule is not in the KB"
            else:
                fact_or_rule = found_rule
                statement = "("
                for my_statement in fact_or_rule.lhs:
                    statement += str(my_statement) + ", "
                statement = statement[:-2]
                statement += ") -> " + str(fact_or_rule.rhs)
        elif isinstance(fact_or_rule, Fact):
            found_fact = self._get_fact(fact_or_rule)
            if not found_fact:
                return "Fact is not in the KB"
            else:
                fact_or_rule = found_fact
                statement = str(fact_or_rule.statement)

        output += " " * (level * 4) + fact_or_rule.name + ": " + statement
        output += " ASSERTED\n" if fact_or_rule.asserted else "\n"
        if fact_or_rule.supported_by:
            for pair in fact_or_rule.supported_by:
                output += " " * (level * 4 + 2) + "SUPPORTED BY\n"
                output += self.kb_explain_helper(pair[0], level + 1) + self.kb_explain_helper(pair[1], level + 1)

        return output


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

        binding = match(rule.lhs[0], fact.statement)
        if binding:
            print(len(rule.lhs))
            if len(rule.lhs) == 1:
                new_fact = Fact(instantiate(rule.rhs, binding), [(fact, rule)])
                rule.supports_facts.append(new_fact)
                fact.supports_facts.append(new_fact)
                print('Adding a new fact:')
                print(new_fact)
                kb.kb_add(new_fact)
            else:
                print('Adding a new rule:')
                lhs_list = [instantiate(element, binding) for element in rule.lhs[1:]]
                rhs = instantiate(rule.rhs, binding)
                # print('lhs_list', lhs_list)
                # print('rhs', rule.rhs)
                new_rule = Rule([lhs_list, rhs], [(fact, rule)])
                print(new_rule)
                rule.supports_rules.append(new_rule)
                fact.supports_rules.append(new_rule)
                kb.kb_add(new_rule)
                # print(instantiate(rule.lhs[1:], binding))
